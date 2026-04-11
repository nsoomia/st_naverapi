import { useState, useEffect } from 'react';
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import {
  Plane, TrendingUp, Globe, AlertCircle, MessageSquare, Star
} from 'lucide-react';
import type { DashboardData } from './types';
import './index.css';

const TABS = [
  { id: 'historical', name: '항공 시장 추세', icon: TrendingUp },
  { id: 'target', name: '타겟 도시 모니터링', icon: Globe },
  { id: 'eda', name: '종합 핵심 지표', icon: Star },
  { id: 'product', name: '상품 및 리스크', icon: AlertCircle },
  { id: 'review', name: '일정 및 리뷰 분석', icon: MessageSquare },
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

export default function App() {
  const [activeTab, setActiveTab] = useState('historical');
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('./data/dashboard_data.json')
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load data", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-950 text-white">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-brand-primary"></div>
      </div>
    );
  }

  if (!data) return <div>데이터를 불러오는데 실패했습니다.</div>;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 font-sans">
      {/* Sidebar / Navigation */}
      <div className="flex h-screen overflow-hidden">
        <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
          <div className="p-6">
            <h1 className="text-2xl font-bold gradient-text flex items-center gap-2">
              <Plane className="text-brand-primary" />
              HanaTour Bio
            </h1>
            <p className="text-xs text-slate-400 mt-1">Aviation & Travel Dashboard</p>
          </div>

          <nav className="flex-1 px-4 space-y-2 mt-4">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === tab.id
                  ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                  }`}
              >
                <tab.icon size={20} />
                <span className="font-medium text-sm">{tab.name}</span>
              </button>
            ))}
          </nav>

          <div className="p-4 border-t border-slate-800">
            <div className="glass-card p-3 text-xs text-slate-400">
              © 2026 Hanatour Analytics
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-8">
          <header className="mb-8 flex justify-between items-center text-left">
            <div>
              <h2 className="text-3xl font-bold">{TABS.find(t => t.id === activeTab)?.name}</h2>
              <p className="text-slate-400 mt-1">실시간 데이터 분석 및 비즈니스 인사이트</p>
            </div>
            <div className="flex gap-4">
              <div className="glass-card py-2 px-4 flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span className="text-sm font-medium">Live System</span>
              </div>
            </div>
          </header>

          {/* Tab Content */}
          <div className="space-y-8 text-left">
            {activeTab === 'historical' && <HistoricalView data={data} />}
            {activeTab === 'target' && <TargetCityView data={data} />}
            {activeTab === 'eda' && <EDAView data={data} />}
            {activeTab === 'product' && <ProductRiskView data={data} />}
            {activeTab === 'review' && <ReviewInsightView data={data} />}
          </div>
        </main>
      </div>
    </div>
  );
}

// --- Tab Components ---

function HistoricalView({ data }: { data: DashboardData }) {
  const chartData = data.aviation_monthly.map(d => ({
    name: `${d.연도}.${d.월}`,
    passengers: d["여객_계(명)"]
  })).slice(-24); // Last 24 months

  return (
    <div className="grid grid-cols-1 gap-6">
      <div className="glass-card">
        <h3 className="text-xl font-semibold mb-6">코로나 이후 연도별/월별 항공 여객 추이</h3>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorPass" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0046ff" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#0046ff" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }}
                itemStyle={{ color: '#00d4ff' }}
              />
              <Area type="monotone" dataKey="passengers" stroke="#0046ff" fillOpacity={1} fill="url(#colorPass)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <p className="mt-4 text-sm text-slate-400">
          * 엔데믹 이후 항공 여객 수가 점진적으로 회복되고 있으며, 최근 2025년 실적은 코로나 이전 수준에 근접하고 있습니다.
        </p>
      </div>
    </div>
  );
}

function TargetCityView({ data }: { data: DashboardData }) {
  const cities = ['다낭', '나트랑', '싱가포르'];
  // Group data by Month for multi-line
  const timeline = Array.from(new Set(data.aviation_target.map(d => `${d.연도}.${d.월}`))).slice(-12);
  const chartData = timeline.map(t => {
    const item: any = { name: t };
    cities.forEach(c => {
      const found = data.aviation_target.find(d => `${d.연도}.${d.월}` === t && d.도시_norm === c);
      item[c] = found ? found["여객_계(명)"] : 0;
    });
    return item;
  });

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="glass-card lg:col-span-2">
        <h3 className="text-xl font-semibold mb-6">타겟 도시(다낭, 나트랑, 싱가포르) 항공 실적 비교</h3>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b' }} />
              <Legend />
              <Line type="monotone" dataKey="다낭" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 8 }} />
              <Line type="monotone" dataKey="나트랑" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="싱가포르" stroke="#f59e0b" strokeWidth={3} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {data.city_metrics.map((city, idx) => (
        <div key={idx} className="glass-card flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">{city.대상도시}</p>
            <p className="text-2xl font-bold mt-1">{city.리뷰수.toLocaleString()}건</p>
          </div>
          <div className="text-right">
            <p className="text-slate-400 text-sm">평균 평점</p>
            <div className="flex items-center gap-1 mt-1">
              <span className="text-2xl font-bold text-yellow-400">{city.평점.toFixed(2)}</span>
              <Star className="text-yellow-400 fill-yellow-400" size={20} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function EDAView({ data }: { data: DashboardData }) {
  const pieData = Object.entries(data.rating_distribution).map(([name, value]) => ({ name: `${name}점`, value }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="glass-card">
        <h3 className="text-xl font-semibold mb-6">전체 평점 분포</h3>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
              >
                {pieData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass-card">
        <h3 className="text-xl font-semibold mb-6">동행자 유형별 만족도</h3>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.companion_rating} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis type="number" domain={[4, 5]} stroke="#64748b" />
              <YAxis dataKey="동행" type="category" stroke="#64748b" width={80} />
              <Tooltip />
              <Bar dataKey="평점" fill="#0046ff" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function ProductRiskView({ data }: { data: DashboardData }) {
  const chartData = data.length_by_rating;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="glass-card lg:col-span-2">
        <h3 className="text-xl font-semibold mb-6">평점별 평균 리뷰 길이 (불만 고객 분석)</h3>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="평점" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip />
              <Bar dataKey="리뷰길이" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <p className="mt-4 text-sm text-slate-400">
          * 평점이 낮을수록 리뷰의 길이가 길어지는 경향을 보입니다 (분노의 장문 폭로). 1~3점대 고객의 페인포인트 집중 관리가 필요합니다.
        </p>
      </div>

      <div className="glass-card bg-red-950/20 border-red-900/50">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2 text-red-400">
          <AlertCircle size={24} />
          도시별 저평점(Risk) 비중
        </h3>
        <div className="space-y-4">
          {data.city_metrics.map((city, idx) => (
            <div key={idx}>
              <div className="flex justify-between text-sm mb-1">
                <span>{city.대상도시}</span>
                <span className="font-bold text-red-400">{(city.저평점 * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2">
                <div
                  className="bg-red-500 h-2 rounded-full"
                  style={{ width: `${city.저평점 * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ReviewInsightView({ data }: { data: DashboardData }) {
  const ageData = Object.entries(data.age_distribution).map(([name, value]) => ({ name: `${name}0대`, value }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="glass-card">
        <h3 className="text-xl font-semibold mb-6">연령대별 리뷰 분포</h3>
        <div className="flex flex-wrap gap-4 items-center justify-center h-[300px]">
          {ageData.map((d, i) => (
            <div key={i} className="flex flex-col items-center">
              <div
                className="rounded-full flex items-center justify-center text-white font-bold transition-transform hover:scale-110 cursor-default"
                style={{
                  width: `${Math.sqrt(d.value) * 5}px`,
                  height: `${Math.sqrt(d.value) * 5}px`,
                  backgroundColor: COLORS[i % COLORS.length],
                  minWidth: '60px',
                  minHeight: '60px'
                }}
              >
                {d.name}
              </div>
              <span className="mt-2 text-xs text-slate-400">{d.value}건</span>
            </div>
          ))}
        </div>
      </div>

      <div className="glass-card">
        <h3 className="text-xl font-semibold mb-6">검출된 핵심 키워드</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-green-950/20 rounded-xl border border-green-900/50">
            <h4 className="text-green-400 font-bold mb-3 flex items-center gap-2">
              <Star size={16} /> 긍정 키워드
            </h4>
            <div className="flex flex-wrap gap-2">
              {data.keywords.긍정.map((k, i) => (
                <span key={i} className="px-2 py-1 bg-green-900/30 text-green-300 text-xs rounded-lg">{k}</span>
              ))}
            </div>
          </div>
          <div className="p-4 bg-red-950/20 rounded-xl border border-red-900/50">
            <h4 className="text-red-400 font-bold mb-3 flex items-center gap-2">
              <AlertCircle size={16} /> 부정 키워드
            </h4>
            <div className="flex flex-wrap gap-2">
              {data.keywords.부정.map((k, i) => (
                <span key={i} className="px-2 py-1 bg-red-900/30 text-red-300 text-xs rounded-lg">{k}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
