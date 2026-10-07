import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import toast from 'react-hot-toast'
import interviewsService from '../../services/interviews.service'

const TYPE_COLORS = {
  technical: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  coding: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  behavioral: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  hr: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  project: 'bg-pink-500/20 text-pink-300 border-pink-500/30',
}

function useVoiceInput(onTranscript) {
  const recognitionRef = useRef(null)
  const [isListening, setIsListening] = useState(false)
  const [supported, setSupported] = useState(false)

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition
    setSupported(!!SpeechRecognition)
    if (!SpeechRecognition) return

    const rec = new SpeechRecognition()
    rec.continuous = true
    rec.interimResults = true
    rec.lang = 'en-US'

    rec.onresult = (e) => {
      const transcript = Array.from(e.results)
        .map((r) => r[0].transcript)
        .join('')
      onTranscript(transcript)
    }

    rec.onend = () => setIsListening(false)
    rec.onerror = () => setIsListening(false)

    recognitionRef.current = rec
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const toggle = useCallback(() => {
    const rec = recognitionRef.current
    if (!rec) return
    if (isListening) {
      rec.stop()
      setIsListening(false)
    } else {
      rec.start()
      setIsListening(true)
    }
  }, [isListening])

  const stop = useCallback(() => {
    recognitionRef.current?.stop()
    setIsListening(false)
  }, [])

  return { isListening, supported, toggle, stop }
}

function ConfirmModal({ onConfirm, onCancel }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-gray-900 border border-white/10 rounded-xl p-6 max-w-sm w-full mx-4">
        <h3 className="text-base font-semibold text-white mb-2">End interview early?</h3>
        <p className="text-sm text-gray-400 mb-5">
          Your progress will be saved. You can still complete the interview from your history.
        </p>
        <div className="flex gap-3">
          <button
            onClick={onCancel}
            className="flex-1 py-2 rounded-lg border border-white/10 text-sm text-gray-300 hover:border-white/30"
          >
            Continue
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-sm text-white font-medium"
          >
            End Interview
          </button>
        </div>
      </div>
    </div>
  )
}

function FeedbackPanel({ feedback, onNext, isLast }) {
  const score = feedback.score || 0
  const color =
    score >= 80
      ? 'text-emerald-400'
      : score >= 60
      ? 'text-blue-400'
      : score >= 40
      ? 'text-amber-400'
      : 'text-red-400'

  return (
    <div className="bg-gray-900 border border-white/10 rounded-xl p-5 space-y-4 mt-4">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-white">Answer Feedback</span>
        <span className={`text-lg font-bold ${color}`}>{Math.round(score)}/100</span>
      </div>

      <p className="text-sm text-gray-300 leading-relaxed">{feedback.feedback}</p>

      {feedback.strengths?.length > 0 && (
        <div>
          <p className="text-xs font-medium text-emerald-400 mb-1">✅ Strengths</p>
          <ul className="space-y-1">
            {feedback.strengths.map((s, i) => (
              <li key={i} className="text-xs text-gray-300 flex gap-1.5">
                <span className="text-emerald-500 mt-0.5">•</span> {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      {feedback.weaknesses?.length > 0 && (
        <div>
          <p className="text-xs font-medium text-amber-400 mb-1">⚠️ To improve</p>
          <ul className="space-y-1">
            {feedback.weaknesses.map((w, i) => (
              <li key={i} className="text-xs text-gray-300 flex gap-1.5">
                <span className="text-amber-500 mt-0.5">•</span> {w}
              </li>
            ))}
          </ul>
        </div>
      )}

      {feedback.better_answer_example && (
        <div className="bg-gray-800 rounded-lg p-3">
          <p className="text-xs font-medium text-blue-300 mb-1">💡 Hint</p>
          <p className="text-xs text-gray-300 leading-relaxed">{feedback.better_answer_example}</p>
        </div>
      )}

      <button
        onClick={onNext}
        className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition-all"
      >
        {isLast ? 'View Results →' : 'Next Question →'}
      </button>
    </div>
  )
}

export default function InterviewSession() {
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()

  const [interview, setInterview] = useState(location.state?.interview || null)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [totalQuestions, setTotalQuestions] = useState(0)
  const [answeredCount, setAnsweredCount] = useState(0)
  const [answer, setAnswer] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [feedback, setFeedback] = useState(null)
  const [showConfirm, setShowConfirm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [elapsed, setElapsed] = useState(0)
  const timerRef = useRef(null)

  const { isListening, supported: voiceSupported, toggle: toggleVoice, stop: stopVoice } =
    useVoiceInput((transcript) => setAnswer(transcript))

  // Timer
  useEffect(() => {
    timerRef.current = setInterval(() => setElapsed((e) => e + 1), 1000)
    return () => clearInterval(timerRef.current)
  }, [])

  const formatTime = (s) => {
    const m = Math.floor(s / 60)
    const sec = s % 60
    return `${m}:${sec.toString().padStart(2, '0')}`
  }

  // Load first question
  useEffect(() => {
    const loadQuestion = async () => {
      try {
        if (interview?.first_question) {
          setCurrentQuestion(interview.first_question)
          setTotalQuestions(interview.total_questions || 0)
          setAnsweredCount(interview.answered_questions || 0)
          setLoading(false)
          return
        }
        // Fetch from API
        const res = await interviewsService.nextQuestion(id)
        const data = res.data
        if (data.done) {
          navigate(`/interview/${id}/results`)
          return
        }
        setCurrentQuestion(data)
        setTotalQuestions(data.total_questions || 0)
        setLoading(false)
      } catch {
        toast.error('Failed to load interview.')
        navigate('/interview')
      }
    }
    loadQuestion()
  }, [id]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSubmit = async () => {
    if (answer.trim().length < 10) {
      toast.error('Please write at least a short answer before submitting.')
      return
    }
    if (isListening) stopVoice()
    setSubmitting(true)
    try {
      const res = await interviewsService.submitAnswer(id, answer.trim())
      const result = res.data
      setFeedback(result)
      setAnsweredCount((c) => c + 1)
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to submit answer.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleNext = async () => {
    setFeedback(null)
    setAnswer('')

    const nextQ = feedback?.next_question
    if (!nextQ) {
      // All done — complete
      await handleComplete()
      return
    }
    setCurrentQuestion(nextQ)
  }

  const handleComplete = async () => {
    try {
      await interviewsService.complete(id)
      navigate(`/interview/${id}/results`)
    } catch {
      navigate(`/interview/${id}/results`)
    }
  }

  const handleEndEarly = async () => {
    setShowConfirm(false)
    navigate('/interview/history')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const questionNum = currentQuestion?.question_number || answeredCount + 1
  const progress = totalQuestions > 0 ? (answeredCount / totalQuestions) * 100 : 0
  const qType = currentQuestion?.question_type || 'technical'
  const typeColor = TYPE_COLORS[qType] || TYPE_COLORS.technical

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
      {showConfirm && (
        <ConfirmModal
          onConfirm={handleEndEarly}
          onCancel={() => setShowConfirm(false)}
        />
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold text-white">
            {interview?.target_career || 'Interview Session'}
          </h1>
          <p className="text-xs text-gray-500 capitalize">
            {interview?.interview_type?.replace('_', ' ')} · {interview?.difficulty}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-500 tabular-nums">{formatTime(elapsed)}</span>
          <button
            onClick={() => setShowConfirm(true)}
            className="text-xs text-red-400 hover:text-red-300 border border-red-500/30 hover:border-red-400/50 px-3 py-1.5 rounded-lg transition"
          >
            End Early
          </button>
        </div>
      </div>

      {/* Progress bar */}
      <div>
        <div className="flex justify-between text-xs text-gray-500 mb-1.5">
          <span>Question {questionNum} of {totalQuestions}</span>
          <span>{answeredCount} answered</span>
        </div>
        <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-500 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Question card */}
      {currentQuestion && !feedback && (
        <div className="bg-gray-900 border border-white/10 rounded-xl p-6 space-y-5">
          <div className="flex items-start justify-between gap-4">
            <span
              className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-md border ${typeColor}`}
            >
              {qType.charAt(0).toUpperCase() + qType.slice(1)}
            </span>
            {currentQuestion.topic && (
              <span className="text-xs text-gray-500">{currentQuestion.topic}</span>
            )}
          </div>

          <p className="text-base text-white leading-relaxed font-medium">
            {currentQuestion.question_text}
          </p>

          {/* Answer input */}
          <div className="space-y-2">
            <div className="relative">
              <textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                rows={6}
                placeholder="Type your answer here… (minimum ~50 characters for a complete response)"
                className="w-full bg-gray-800 border border-white/10 text-white rounded-lg px-4 py-3 text-sm resize-none focus:outline-none focus:border-blue-500 transition"
              />
              {answer.length > 0 && (
                <span className="absolute bottom-2.5 right-3 text-xs text-gray-600">
                  {answer.length} chars
                </span>
              )}
            </div>

            {/* Voice input */}
            <div className="flex items-center gap-2">
              {voiceSupported ? (
                <button
                  onClick={toggleVoice}
                  className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border transition ${
                    isListening
                      ? 'bg-red-500/20 border-red-500/50 text-red-300 animate-pulse'
                      : 'bg-gray-800 border-white/10 text-gray-400 hover:border-white/30'
                  }`}
                >
                  <span>{isListening ? '🔴' : '🎙️'}</span>
                  {isListening ? 'Listening… (click to stop)' : 'Use voice input'}
                </button>
              ) : (
                <span className="text-xs text-gray-600">
                  🎙️ Voice input not available in this browser
                </span>
              )}
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={submitting || answer.trim().length < 10}
            className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition-all"
          >
            {submitting ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Evaluating…
              </span>
            ) : (
              'Submit Answer'
            )}
          </button>
        </div>
      )}

      {/* Feedback panel */}
      {feedback && (
        <FeedbackPanel
          feedback={feedback}
          onNext={handleNext}
          isLast={!feedback.next_question}
        />
      )}
    </div>
  )
}
