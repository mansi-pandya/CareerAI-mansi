import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import LearningResourceCard from '../../components/career/LearningResourceCard'
import CareerService from '../../services/career.service'

const DIFFICULTIES = ['all', 'beginner', 'intermediate', 'advanced']
const PROVIDERS = ['all', 'freeCodeCamp', 'Coursera', 'Kaggle Learn', 'Google', 'IBM SkillsBuild', 'AWS Skill Builder', 'Microsoft Learn', 'Official Docs']

export default function LearningResources() {
  const [searchParams] = useSearchParams()
  const initialSkill = searchParams.get('skill') || ''

  const [resources, setResources] = useState([])
  const [loading, setLoading] = useState(true)
  const [skillFilter, setSkillFilter] = useState(initialSkill)
  const [diffFilter, setDiffFilter] = useState('all')
  const [providerFilter, setProviderFilter] = useState('all')
  const [freeOnly, setFreeOnly] = useState(false)
  const [searchInput, setSearchInput] = useState(initialSkill)

  useEffect(() => {
    fetchResources()
  }, [])

  async function fetchResources() {
    setLoading(true)
    try {
      let data
      if (initialSkill) {
        data = await CareerService.getResourcesForSkill(initialSkill)
        if (!data?.length) {
          data = await CareerService.getLearningResources()
        }
      } else {
        data = await CareerService.getLearningResources()
      }
      // Fallback to full library if nothing from gaps
      if (!data?.length) {
        data = await CareerService.getLearningResources()
      }
      setResources(data || [])
    } catch {
      toast.error('Failed to load learning resources')
    } finally {
      setLoading(false)
    }
  }

  async function handleSkillSearch() {
    if (!searchInput.trim()) {
      fetchResources()
      return
    }
    setLoading(true)
    try {
      const data = await CareerService.getResourcesForSkill(searchInput.trim())
      setResources(data)
      setSkillFilter(searchInput.trim())
    } catch {
      toast.error('No resources found for that skill')
    } finally {
      setLoading(false)
    }
  }

  const filtered = resources.filter((r) => {
    if (skillFilter && !r.skill_name?.toLowerCase().includes(skillFilter.toLowerCase()) &&
        !r.topics?.some((t) => t.toLowerCase().includes(skillFilter.toLowerCase()))) return false
    if (diffFilter !== 'all' && r.difficulty !== diffFilter) return false
    if (providerFilter !== 'all' && !r.provider?.includes(providerFilter)) return false
    if (freeOnly && !r.is_free) return false
    return true
  })

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Learning Resources</h1>
        <p className="text-gray-400 text-sm mt-1">
          Curated, real resources from IBM, Google, AWS, Microsoft, Kaggle, freeCodeCamp and more.
        </p>
      </div>

      {/* Filters */}
      <Card>
        <Card.Body>
          <div className="flex flex-wrap gap-3 items-end">
            {/* Skill search */}
            <div className="flex-1 min-w-[200px]">
              <label className="block text-xs text-gray-400 mb-1">Search by skill</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSkillSearch()}
                  placeholder="e.g. python, react, docker…"
                  className="flex-1 bg-gray-800 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
                />
                <Button size="sm" onClick={handleSkillSearch}>Search</Button>
              </div>
            </div>
            {/* Difficulty */}
            <div>
              <label className="block text-xs text-gray-400 mb-1">Difficulty</label>
              <select
                value={diffFilter}
                onChange={(e) => setDiffFilter(e.target.value)}
                className="bg-gray-800 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              >
                {DIFFICULTIES.map((d) => (
                  <option key={d} value={d}>{d === 'all' ? 'All Levels' : d.charAt(0).toUpperCase() + d.slice(1)}</option>
                ))}
              </select>
            </div>
            {/* Free toggle */}
            <label className="flex items-center gap-2 cursor-pointer pb-1">
              <div
                className={`w-9 h-5 rounded-full transition-colors ${freeOnly ? 'bg-blue-600' : 'bg-gray-700'}`}
                onClick={() => setFreeOnly((v) => !v)}
              >
                <div className={`w-3.5 h-3.5 m-0.5 rounded-full bg-white transition-transform ${freeOnly ? 'translate-x-4' : ''}`} />
              </div>
              <span className="text-sm text-gray-300">Free only</span>
            </label>
            {/* Clear */}
            {(skillFilter || diffFilter !== 'all' || freeOnly) && (
              <Button
                size="sm"
                variant="ghost"
                onClick={() => {
                  setSkillFilter('')
                  setSearchInput('')
                  setDiffFilter('all')
                  setFreeOnly(false)
                  fetchResources()
                }}
              >
                Clear filters
              </Button>
            )}
          </div>
        </Card.Body>
      </Card>

      {/* Count */}
      <div className="text-sm text-gray-400">
        Showing <span className="text-white font-medium">{filtered.length}</span> resource{filtered.length !== 1 ? 's' : ''}
        {skillFilter && <span> for <span className="text-blue-400 font-medium">{skillFilter}</span></span>}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : filtered.length === 0 ? (
        <Card>
          <Card.Body className="text-center py-12">
            <div className="text-3xl mb-3">📚</div>
            <p className="text-white font-semibold">No resources found</p>
            <p className="text-gray-400 text-sm mt-1">Try a different skill name or adjust the filters.</p>
          </Card.Body>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((r, i) => (
            <LearningResourceCard key={i} resource={r} />
          ))}
        </div>
      )}
    </div>
  )
}
