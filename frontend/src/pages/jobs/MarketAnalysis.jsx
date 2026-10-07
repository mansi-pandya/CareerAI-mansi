import { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import JobsService from '../../services/jobs.service'

const PIE_COLORS = ['#3b82f6', '#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899']

function SectionTitle({ children }) {
  return (
    <h2 className="text-base font-semibold text-gray-200 mb-4">{children}</h2>
  )
}

function StatCard({ label, value, sub, color = 'blue' }) {
  const colors = {
    blue: 'from-blue-600/20 to-indigo-600/20 border-blue-500/20',
    green: 'from-emerald-600/20 to-teal-600/20 border-emerald-500/20',
    purple: 'from-purple-600/20 to-violet-600/20 border-purple-500/20',
    orange: 'from-orange-600/20 to-amber-600/20 border-orange-500/20',
  }
  return (
    <div className={`bg-gradient-to-br ${colors[color]} border rounded-xl p-4`}>
      <p className="text-2xl font-bold text-white tabular-nums">{value}</p>
      <p className="text-sm font-medium text-gray-300 mt-0.5">{label}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  )
}

function CustomBarTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div className="bg-gray-800 border border-white/10 rounded-lg px-3 py-2 text-sm shadow-xl">
      <p className="font-medium text-white">{d.skill}</p>
      <p className="text-blue-400">{d.demand_percentage}% of jobs</p>
      <p className="text-gray-500">{d.count} listings</p>
      {d.have_skill !== undefined && (
        <p className={d.have_skill ? 'text-emerald-400' : 'text-gray-500'}>
          {d.have_skill ? '✓ You have this skill' : '✗ Skill gap'}
        </p>
      )}
    </div>
  )
}

function CustomPieTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-gray-800 border border-white/10 rounded-lg px-3 py-2 text-sm shadow-xl">
      <p className="font-medium text-white">{payload[0].name}</p>
      <p className="text-blue-400">{payload[0].value}%</p>
    </div>
  )
}

export default function MarketAnalysis() {
  const [skills, setSkills] = useState(null)
  const [trends, setTrends] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const [s, t] = await Promise.all([
          JobsService.getMarketSkills(),
          JobsService.getMarketTrends(),
        ])
        setSkills(s)
        setTrends(t)
      } catch {
        toast.error('Failed to load market data')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="p-6 space-y-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-40 rounded-xl bg-gray-900 border border-white/6 animate-pulse" />
        ))}
      </div>
    )
  }

  const topSkills = skills?.top_skills || []
  const mySkills = skills?.my_skills_in_demand || []
  const missingSkills = skills?.missing_high_demand_skills || []
  const totalJobs = skills?.total_jobs_analyzed || 0

  const jobTypeTrends = trends?.job_type_trends || []
  const workModeTrends = trends?.work_mode_trends || []
  const topCompanies = trends?.top_companies || []

  const pieJobType = jobTypeTrends.map((t) => ({ name: t.label, value: t.percentage }))
  const pieWorkMode = workModeTrends.map((t) => ({ name: t.label, value: t.percentage }))

  // Color bars based on have_skill
  const barData = topSkills.map((s) => ({
    ...s,
    fill: s.have_skill ? '#10b981' : '#3b82f6',
  }))

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="px-6 py-6 border-b border-white/6">
        <h1 className="text-2xl font-bold text-white mb-1">Market Skill Analysis</h1>
        <p className="text-sm text-gray-400">
          Understand what skills employers demand and where you stand
        </p>
      </div>

      <div className="px-6 py-6 space-y-8 max-w-5xl">
        {/* Stats row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <StatCard label="Jobs Analyzed" value={totalJobs} color="blue" />
          <StatCard label="Top Skills Tracked" value={topSkills.length} color="indigo" />
          <StatCard
            label="Skills You Have"
            value={mySkills.length}
            sub="in top 20 demand"
            color="green"
          />
          <StatCard
            label="Skill Gaps"
            value={missingSkills.length}
            sub="high-demand, missing"
            color="orange"
          />
        </div>

        {/* Top 20 Skills Bar Chart */}
        {topSkills.length > 0 && (
          <div className="bg-gray-900 border border-white/6 rounded-xl p-6">
            <SectionTitle>Top {topSkills.length} In-Demand Skills</SectionTitle>
            <p className="text-xs text-gray-500 mb-4 flex items-center gap-4">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500 inline-block" />
                Skills you have
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-blue-500 inline-block" />
                Skills you don't have
              </span>
            </p>
            <ResponsiveContainer width="100%" height={360}>
              <BarChart
                data={barData}
                layout="vertical"
                margin={{ top: 0, right: 20, left: 80, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" horizontal={false} />
                <XAxis
                  type="number"
                  domain={[0, 100]}
                  tickFormatter={(v) => `${v}%`}
                  tick={{ fill: '#6b7280', fontSize: 11 }}
                  axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
                  tickLine={false}
                />
                <YAxis
                  type="category"
                  dataKey="skill"
                  tick={{ fill: '#9ca3af', fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                  width={80}
                />
                <Tooltip content={<CustomBarTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
                <Bar dataKey="demand_percentage" radius={[0, 4, 4, 0]}>
                  {barData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} fillOpacity={0.85} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* My Skills vs Market */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Skills I have */}
          <div className="bg-gray-900 border border-white/6 rounded-xl p-5">
            <SectionTitle>Skills You Have in Demand</SectionTitle>
            {mySkills.length === 0 ? (
              <p className="text-sm text-gray-500">
                Complete your profile to see your skill overlap with market demand.
              </p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {mySkills.map((skill) => (
                  <span
                    key={skill}
                    className="px-3 py-1 text-sm rounded-full bg-emerald-900/30 border border-emerald-500/40 text-emerald-300"
                  >
                    ✓ {skill}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Skills missing */}
          <div className="bg-gray-900 border border-white/6 rounded-xl p-5">
            <SectionTitle>High-Demand Skills You're Missing</SectionTitle>
            {missingSkills.length === 0 ? (
              <p className="text-sm text-gray-500">
                Great work! You have all the high-demand skills (or complete your profile to see gaps).
              </p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {missingSkills.map((skill) => (
                  <span
                    key={skill}
                    className="px-3 py-1 text-sm rounded-full bg-red-900/25 border border-red-500/30 text-red-300"
                  >
                    ✗ {skill}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Job Type + Work Mode Trends */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Job Type Pie */}
          {pieJobType.length > 0 && (
            <div className="bg-gray-900 border border-white/6 rounded-xl p-5">
              <SectionTitle>Job Type Distribution</SectionTitle>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={pieJobType}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieJobType.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomPieTooltip />} />
                  <Legend
                    formatter={(value) => (
                      <span style={{ color: '#9ca3af', fontSize: 12 }}>{value}</span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Work Mode Pie */}
          {pieWorkMode.length > 0 && (
            <div className="bg-gray-900 border border-white/6 rounded-xl p-5">
              <SectionTitle>Work Mode Distribution</SectionTitle>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={pieWorkMode}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieWorkMode.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomPieTooltip />} />
                  <Legend
                    formatter={(value) => (
                      <span style={{ color: '#9ca3af', fontSize: 12 }}>{value}</span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Top Hiring Companies */}
        {topCompanies.length > 0 && (
          <div className="bg-gray-900 border border-white/6 rounded-xl p-5">
            <SectionTitle>Top Hiring Companies</SectionTitle>
            <div className="space-y-2">
              {topCompanies.map((c, i) => (
                <div key={c.company} className="flex items-center gap-3">
                  <span className="w-6 text-xs text-gray-600 text-right shrink-0">#{i + 1}</span>
                  <div className="flex-1 flex items-center justify-between">
                    <span className="text-sm text-gray-300">{c.company}</span>
                    <span className="text-xs text-gray-500">{c.job_count} listing{c.job_count !== 1 ? 's' : ''}</span>
                  </div>
                  {/* mini bar */}
                  <div className="w-24 bg-white/6 rounded-full h-1.5">
                    <div
                      className="h-1.5 rounded-full bg-blue-500/60"
                      style={{ width: `${Math.min(100, (c.job_count / (topCompanies[0]?.job_count || 1)) * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
