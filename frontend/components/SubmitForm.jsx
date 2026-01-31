'use client'

import { useState } from 'react'

const ADDICTION_TYPES = [
  { value: 'alcohol', label: 'Alcohol' },
  { value: 'drugs', label: 'Drugs' },
  { value: 'gambling', label: 'Gambling' },
  { value: 'smoking', label: 'Smoking' },
  { value: 'other', label: 'Other' },
]

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function SubmitForm() {
  const [addictionType, setAddictionType] = useState('')
  const [telegramChatId, setTelegramChatId] = useState('')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setStatus(null)

    const cleanChatId = telegramChatId.trim()
    if (!cleanChatId) {
      setStatus({
        type: 'error',
        message: 'Please enter your Telegram chat ID',
      })
      setLoading(false)
      return
    }

    try {
      const response = await fetch(`${API_URL}/api/send-support`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          addiction_type: addictionType,
          telegram_chat_id: cleanChatId,
        }),
      })

      const data = await response.json()

      if (response.ok && data.success) {
        setStatus({
          type: 'success',
          message: 'Support message sent! Check your Telegram.',
        })
        setAddictionType('')
        setTelegramChatId('')
      } else {
        setStatus({
          type: 'error',
          message: data.detail || 'Something went wrong. Please try again.',
        })
      }
    } catch (error) {
      setStatus({
        type: 'error',
        message: 'Could not connect to server. Please try again.',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <label
          htmlFor="addiction-type"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          What are you recovering from?
        </label>
        <select
          id="addiction-type"
          value={addictionType}
          onChange={(e) => setAddictionType(e.target.value)}
          required
          className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-gray-800"
        >
          <option value="">Select an option</option>
          {ADDICTION_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label
          htmlFor="telegram-id"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Telegram Chat ID
        </label>
        <input
          type="text"
          id="telegram-id"
          value={telegramChatId}
          onChange={(e) => setTelegramChatId(e.target.value)}
          placeholder="123456789"
          required
          className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-gray-800"
        />
        <p className="text-xs text-gray-500 mt-1">
          Message @userinfobot on Telegram to get your chat ID
        </p>
      </div>

      {status && (
        <div
          className={`p-4 rounded-lg ${
            status.type === 'success'
              ? 'bg-green-50 text-green-800 border border-green-200'
              : 'bg-red-50 text-red-800 border border-red-200'
          }`}
        >
          {status.message}
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 px-4 bg-gradient-to-r from-primary to-secondary text-white font-semibold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <span className="flex items-center justify-center">
            <svg
              className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Sending...
          </span>
        ) : (
          'Send Support Message'
        )}
      </button>
    </form>
  )
}
