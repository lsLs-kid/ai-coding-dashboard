import { useEffect, useState } from "react";
import { BarChart3, ChevronDown, Coins, Loader2, TrendingUp, Users } from "lucide-react";
import ReactECharts from "echarts-for-react";
import { defaultCostFilters, getCostTokens, getCostOverview, getFilterOptions } from "../api";
import type {
  CostFilters,
  CostOverview,
  CostTrendPoint,
  FilterOptions,
  ModelCostStats,
  PduCostStats,
  TokenPageResponse,
} from "../types";

const costKpiIcons = [Coins, TrendingUp, TrendingUp, Users];

const costTypeOptions = [
  { label: "Total Token", value: "total" as const },
  { label: "Input Token", value: "input" as const },
  { label: "Output Token", value: "output" as const },
];

const COST_TYPE_MAP: Record<CostFilters["cost_type"], 0 | 1 | 2> = {
  total: 0,
  input: 1,
  output: 2,
};

export function CostPage({ onUpdatedAt }: { onUpdatedAt: (t: string) => void }) {
  const [filters, setFilters] = useState<CostFilters>(defaultCostFilters);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [overview, setOverview] = useState<CostOverview | null>(null);
  const [tokens, setTokens] = useState<TokenPageResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [tableLoading, setTableLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tableState, setTableState] = useState({
    page: 1,
    sort_by: "date",
    sort_order: "desc" as "asc" | "desc",
  });

  useEffect(() => {
    void bootstrap();
  }, []);

  async function bootstrap() {
    setIsLoading(true);
    setError(null);
    try {
      const [options, ovData, tokData] = await Promise.all([
        getFilterOptions(),
        getCostOverview(filters),
        getCostTokens({ ...filters, ...tableState, cost_type: COST_TYPE_MAP[filters.cost_type], page_size: 20 }),
      ]);
      setFilterOptions(options);
      setOverview(ovData);
      setTokens(tokData);
      onUpdatedAt(new Date().toLocaleString("zh-CN", { hour12: false }).replace(/\//g, "-"));
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setIsLoading(false);
    }
  }

  async function query(nextFilters: CostFilters) {
    setIsLoading(true);
    setError(null);
    const nextTable = { ...tableState, page: 1 };
    setTableState(nextTable);
    try {
      const [ovData, tokData] = await Promise.all([
        getCostOverview(nextFilters),
        getCostTokens({ ...nextFilters, ...nextTable, cost_type: COST_TYPE_MAP[nextFilters.cost_type], page_size: 20 }),
      ]);
      setOverview(ovData);
      setTokens(tokData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "查询失败");
    } finally {
      setIsLoading(false);
    }
  }

  async function fetchTokens(next: typeof tableState, currentFilters: CostFilters) {
    setTableLoading(true);
    try {
      const tokData = await getCostTokens({
        ...currentFilters,
        ...next,
        cost_type: COST_TYPE_MAP[currentFilters.cost_type],
        page_size: 20,
      });
      setTokens(tokData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setTableLoading(false);
    }
  }

  function handleSort(col: string) {
    const nextOrder: "asc" | "desc" =
      tableState.sort_by === col && tableState.sort_order === "desc" ? "asc" : "desc";
    const next = { ...tableState, sort_by: col, sort_order: nextOrder, page: 1 };
    setTableState(next);
    void fetchTokens(next, filters);
  }

  function handlePage(page: number) {
    const next = { ...tableState, page };
    setTableState(next);
    void fetchTokens(next, filters);
  }

  function handleFilterChange(f: CostFilters) {
    setFilters(f);
    void query(f);
  }

  return (
    <>
      <header className="page-header">
        <div>
          <h1>成本分析</h1>
          <p>AI Coding Token 消耗趋势与分布分析</p>
        </div>
      </header>

      <section className="filter-panel">
        {filterOptions ? (
          <CostFilterBar options={filterOptions} filters={filters} onChange={handleFilterChange} />
        ) : (
          <div className="filter-skeleton">筛选项加载中...</div>
        )}
      </section>

      {error ? <div className="error-banner">{error}</div> : null}

      {isLoading && !overview ? (
        <div className="loading-state">
          <Loader2 className="spin" size={28} />
          正在加载成本数据
        </div>
      ) : overview ? (
        <>
          <section className="cost-kpi-grid">
            <CostKpiCard
              label="总 Token 消耗"
              value={overview.kpis.total_tokens.toLocaleString()}
              change={overview.kpis.total_tokens_change}
              accent="blue"
              iconIdx={0}
            />
            <CostKpiCard
              label="Input Token"
              value={overview.kpis.input_tokens.toLocaleString()}
              change={overview.kpis.input_tokens_change}
              accent="cyan"
              iconIdx={1}
            />
            <CostKpiCard
              label="Output Token"
              value={overview.kpis.output_tokens.toLocaleString()}
              change={overview.kpis.output_tokens_change}
              accent="green"
              iconIdx={2}
            />
            <CostKpiCard
              label="人均 Token 消耗"
              value={Math.round(overview.kpis.per_user_tokens).toLocaleString()}
              change={overview.kpis.per_user_tokens_change}
              accent="red"
              iconIdx={3}
            />
          </section>

          <section className="cost-chart-grid">
            <article className="panel">
              <div className="panel-header">
                <h2>
                  Token 消耗趋势<span className="info-dot">i</span>
                </h2>
              </div>
              <ReactECharts option={tokenTrendOption(overview.trend, filters.cost_type)} notMerge style={{ height: 220 }} />
            </article>
            <article className="panel">
              <div className="panel-header">
                <h2>
                  模型 Token 分布<span className="info-dot">i</span>
                </h2>
              </div>
              <ReactECharts option={modelDistributionOption(overview.model_distribution)} notMerge style={{ height: 220 }} />
            </article>
            <article className="panel">
              <div className="panel-header">
                <h2>
                  PDU Token Top 10<span className="info-dot">i</span>
                </h2>
              </div>
              <ReactECharts option={pduTopOption(overview.top_pdus)} notMerge style={{ height: 220 }} />
            </article>
          </section>

          {tokens ? (
            <TokenTable
              response={tokens}
              sortBy={tableState.sort_by}
              sortOrder={tableState.sort_order}
              onSort={handleSort}
              onPage={handlePage}
              loading={tableLoading}
            />
          ) : null}
        </>
      ) : null}
    </>
  );
}

function CostFilterBar({
  options,
  filters,
  onChange,
}: {
  options: FilterOptions;
  filters: CostFilters;
  onChange: (f: CostFilters) => void;
}) {
  const fields = [
    ["时间范围", "date_range", options.date_ranges],
    ["统计粒度", "granularity", options.granularities],
    ["PDU", "pdu", options.pdus],
    ["LM团队", "lm_team", options.lm_teams],
    ["用户", "user", options.users],
    ["端类型", "terminal_type", options.terminal_types],
    ["客户端版本", "client_version", options.client_versions],
    ["IDE类型", "ide_type", options.ide_types],
    ["模型", "model", options.models],
  ] as const;

  return (
    <div className="cost-filter-grid">
      {fields.map(([label, key, items]) => (
        <label key={key} className="filter-field">
          <span>{label}</span>
          <select
            value={filters[key]}
            onChange={(e) => onChange({ ...filters, [key]: e.target.value })}
          >
            {items.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
          <ChevronDown size={14} />
        </label>
      ))}
      <label className="filter-field">
        <span>成本类型</span>
        <select
          value={filters.cost_type}
          onChange={(e) =>
            onChange({ ...filters, cost_type: e.target.value as CostFilters["cost_type"] })
          }
        >
          {costTypeOptions.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <ChevronDown size={14} />
      </label>
    </div>
  );
}

function CostKpiCard({
  label,
  value,
  change,
  accent,
  iconIdx,
}: {
  label: string;
  value: string;
  change: string | null;
  accent: "blue" | "red" | "green" | "cyan";
  iconIdx: number;
}) {
  const Icon = costKpiIcons[iconIdx] ?? BarChart3;
  const direction =
    change == null ? "flat" : change.startsWith("+") ? "up" : change.startsWith("-") ? "down" : "flat";
  return (
    <article className={`kpi-card accent-${accent}`}>
      <div className="kpi-icon">
        <Icon size={28} />
      </div>
      <div>
        <h3>{label}</h3>
        <div className="kpi-value">{value}</div>
        {change ? (
          <p className={`delta ${direction}`}>
            较上期<span> {change}</span>
          </p>
        ) : null}
      </div>
    </article>
  );
}

function TokenTable({
  response,
  sortBy,
  sortOrder,
  onSort,
  onPage,
  loading,
}: {
  response: TokenPageResponse;
  sortBy: string;
  sortOrder: "asc" | "desc";
  onSort: (col: string) => void;
  onPage: (page: number) => void;
  loading: boolean;
}) {
  const totalPages = Math.ceil(response.total / response.page_size);
  const start = Math.max(1, response.page - 2);
  const end = Math.min(totalPages, start + 4);
  const pageNums: number[] = [];
  for (let p = start; p <= end; p++) pageNums.push(p);

  return (
    <section className="panel detail-panel" style={{ opacity: loading ? 0.6 : 1 }}>
      <div className="panel-header" style={{ padding: "14px 0 0" }}>
        <h2>
          Token 明细<span className="info-dot">i</span>
        </h2>
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <SortTh label="日期" col="date" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort} />
            <th>PDU</th>
            <th>LM团队</th>
            <th>用户</th>
            <th>模型</th>
            <SortTh label="Input Token" col="input_tokens" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort} />
            <SortTh label="Output Token" col="output_tokens" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort} />
            <SortTh label="Total Token" col="total_tokens" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort} />
          </tr>
        </thead>
        <tbody>
          {response.items.map((row) => (
            <tr key={row.id}>
              <td>{row.date}</td>
              <td>{row.pdu}</td>
              <td>{row.lm_team}</td>
              <td>{row.user}</td>
              <td>{row.model}</td>
              <td>{row.input_tokens.toLocaleString()}</td>
              <td>{row.output_tokens.toLocaleString()}</td>
              <td>{row.total_tokens.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="table-footer">
        <span>共 {response.total} 条</span>
        <button disabled={response.page <= 1} onClick={() => onPage(response.page - 1)}>
          ‹
        </button>
        {pageNums.map((p) => (
          <button
            key={p}
            className={response.page === p ? "is-active" : ""}
            onClick={() => onPage(p)}
          >
            {p}
          </button>
        ))}
        <button disabled={response.page >= totalPages} onClick={() => onPage(response.page + 1)}>
          ›
        </button>
        <span>每页 {response.page_size} 条</span>
      </div>
    </section>
  );
}

function SortTh({
  label,
  col,
  sortBy,
  sortOrder,
  onSort,
}: {
  label: string;
  col: string;
  sortBy: string;
  sortOrder: "asc" | "desc";
  onSort: (col: string) => void;
}) {
  const arrow = sortBy === col ? (sortOrder === "desc" ? " ↓" : " ↑") : " ↕";
  return (
    <th className="th-sortable" onClick={() => onSort(col)}>
      {label}
      {arrow}
    </th>
  );
}

function baseTextStyle() {
  return { fontFamily: "Inter, Microsoft YaHei, system-ui", color: "#24324a" };
}

function tokenTrendOption(trend: CostTrendPoint[], costType: CostFilters["cost_type"]) {
  const fieldMap = {
    total: { field: "total_tokens" as const, color: "#256ff6", name: "Total Token" },
    input: { field: "input_tokens" as const, color: "#10b99a", name: "Input Token" },
    output: { field: "output_tokens" as const, color: "#ef3445", name: "Output Token" },
  };
  const cfg = fieldMap[costType];
  return {
    grid: { left: 56, right: 20, top: 28, bottom: 42 },
    tooltip: { trigger: "axis" },
    textStyle: baseTextStyle(),
    xAxis: { type: "category", data: trend.map((d) => d.date), axisTick: { show: false } },
    yAxis: { type: "value", name: "Token 数", splitLine: { lineStyle: { color: "#e8edf5" } } },
    series: [
      {
        name: cfg.name,
        data: trend.map((d) => d[cfg.field]),
        type: "line",
        smooth: true,
        symbolSize: 7,
        areaStyle: { color: cfg.color + "1A" },
        lineStyle: { width: 3, color: cfg.color },
        itemStyle: { color: cfg.color },
      },
    ],
  };
}

function modelDistributionOption(models: ModelCostStats[]) {
  const reversed = [...models].sort((a, b) => a.total_tokens - b.total_tokens);
  return {
    tooltip: { trigger: "axis" },
    grid: { left: 120, right: 20, top: 16, bottom: 36 },
    textStyle: baseTextStyle(),
    xAxis: { type: "value", name: "Token 数" },
    yAxis: { type: "category", data: reversed.map((d) => d.model) },
    series: [
      {
        type: "bar",
        data: reversed.map((d) => d.total_tokens),
        itemStyle: { color: "#256ff6", borderRadius: [0, 4, 4, 0] },
      },
    ],
  };
}

function pduTopOption(pdus: PduCostStats[]) {
  const reversed = [...pdus].sort((a, b) => a.total_tokens - b.total_tokens);
  return {
    tooltip: { trigger: "axis" },
    grid: { left: 90, right: 20, top: 16, bottom: 36 },
    textStyle: baseTextStyle(),
    xAxis: { type: "value", name: "Token 数" },
    yAxis: { type: "category", data: reversed.map((d) => d.pdu) },
    series: [
      {
        type: "bar",
        data: reversed.map((d) => d.total_tokens),
        itemStyle: { color: "#10b99a", borderRadius: [0, 4, 4, 0] },
      },
    ],
  };
}
