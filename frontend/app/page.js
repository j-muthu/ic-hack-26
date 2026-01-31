'use client'

import { useState } from 'react'

const RECOVERY_TYPES = [
  { value: 'alcohol', label: 'Alcohol' },
  { value: 'drugs', label: 'Drugs' },
  { value: 'gambling', label: 'Gambling' },
  { value: 'smoking', label: 'Smoking' },
  { value: 'other', label: 'Other' },
]

export default function Home() {
  const [selectedType, setSelectedType] = useState('')

  const telegramLink = selectedType
    ? `https://t.me/Kalm_ai_bot?start=${selectedType}`
    : 'https://t.me/Kalm_ai_bot'

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Kalm</h1>
          <p className="text-white/80 text-lg">
            Your 24/7 recovery companion
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Get Personalized Support
          </h2>
          <p className="text-gray-600 mb-6">
            Tell us what you're recovering from and receive a personalized voice message of support.
          </p>

          <div className="mb-6">
            <label
              htmlFor="recovery-type"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              What are you recovering from?
            </label>
            <select
              id="recovery-type"
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-gray-800 bg-white"
            >
              <option value="">Select an option</option>
              {RECOVERY_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <a
            href={telegramLink}
            target="_blank"
            rel="noopener noreferrer"
            className={`block w-full py-4 px-4 text-white font-semibold rounded-lg transition-all text-center ${
              selectedType
                ? 'bg-[#0088cc] hover:bg-[#0077b5]'
                : 'bg-gray-400 cursor-not-allowed'
            }`}
            onClick={(e) => {
              if (!selectedType) {
                e.preventDefault()
              }
            }}
          >
            <span className="flex items-center justify-center gap-2">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
              </svg>
              {selectedType ? 'Get Support on Telegram' : 'Select what you\'re recovering from'}
            </span>
          </a>

          <div className="mt-6 pt-6 border-t border-gray-100 text-center">
            <p className="text-sm text-gray-500 mb-3">
              Already using Kalm?
            </p>
            <a
              href="https://t.me/Kalm_ai_bot"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#0088cc] hover:underline text-sm font-medium"
            >
              Open Telegram Bot
            </a>
          </div>
        </div>

        <p className="text-center text-white/60 text-sm mt-6">
          You are not alone. Help is always available.
        </p>
      </div>
    </main>
  )
}
