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
  const [otherText, setOtherText] = useState('')

  const isOther = selectedType === 'other'
  const finalType = isOther ? otherText : selectedType
  const isReady = selectedType && (!isOther || otherText.trim())

  const telegramLink = isReady
    ? `https://t.me/Kalm_ai_bot?start=${encodeURIComponent(finalType)}`
    : 'https://t.me/Kalm_ai_bot'

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4 sm:p-6 md:p-8">
      <div className="w-full max-w-[28rem]">
        <div className="text-center mb-6 sm:mb-8">
          <h1 className="text-4xl sm:text-5xl font-semibold text-[#284203] mb-2">Kalm</h1>
          <p className="text-[#284203]/80 text-base sm:text-lg italic">
            Supporting your recovery, one chat at a time
          </p>
        </div>

        <div className="bg-[#d9e4bf] backdrop-blur-sm rounded-2xl shadow-xl p-6 sm:p-8">
          <h2 className="text-lg sm:text-xl font-semibold text-[#284203] mb-2">
            Get Personalized Support
          </h2>
          <p className="text-[#284203]/80 text-sm sm:text-base mb-6">
            Tell us what you're recovering from and receive a personalized voice message of support.
          </p>

          <div className="mb-4 sm:mb-6">
            <label
              htmlFor="recovery-type"
              className="block text-sm font-medium text-[#284203] mb-2"
            >
              What are you recovering from?
            </label>
            <select
              id="recovery-type"
              value={selectedType}
              onChange={(e) => {
                setSelectedType(e.target.value)
                if (e.target.value !== 'other') {
                  setOtherText('')
                }
              }}
              className="w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg border border-[#284203]/30 focus:ring-2 focus:ring-[#284203] focus:border-transparent transition-all text-[#284203] bg-white text-sm sm:text-base"
            >
              <option value="">Select an option</option>
              {RECOVERY_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {isOther && (
            <div className="mb-4 sm:mb-6">
              <label
                htmlFor="other-input"
                className="block text-sm font-medium text-[#284203] mb-2"
              >
                Please specify
              </label>
              <input
                type="text"
                id="other-input"
                value={otherText}
                onChange={(e) => setOtherText(e.target.value)}
                placeholder="e.g., social media, food, etc."
                className="w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg border border-[#284203]/30 focus:ring-2 focus:ring-[#284203] focus:border-transparent transition-all text-[#284203] bg-white text-sm sm:text-base placeholder:text-[#284203]/40"
              />
            </div>
          )}

          <a
            href={telegramLink}
            target="_blank"
            rel="noopener noreferrer"
            className={`block w-full py-3 sm:py-4 px-4 text-[#284203]/80 font-semibold rounded-lg transition-all text-center text-sm sm:text-base ${
              isReady
                ? 'bg-[#7d9f6f] hover:bg-[#6d8f5f]'
                : 'bg-[#7d9f6f]/40 cursor-not-allowed'
            }`}
            onClick={(e) => {
              if (!isReady) {
                e.preventDefault()
              }
            }}
          >
            <span className="flex items-center justify-center gap-2">
              <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
              </svg>
              {isReady ? 'Get Support on Telegram' : isOther ? 'Please specify above' : 'Select what you\'re recovering from'}
            </span>
          </a>

          <div className="relative my-5 sm:my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[#284203]/20"></div>
            </div>
            <div className="relative flex justify-center text-xs sm:text-sm">
              <span className="px-2 bg-[#d9e4bf] text-[#284203]/60">or talk live</span>
            </div>
          </div>

          <a
            href="/talk"
            className="block w-full py-3 sm:py-4 px-4 bg-[#7d9f6f] text-[#284203]/80 font-semibold rounded-lg hover:bg-[#6d8f5f] transition-colors text-center text-sm sm:text-base"
          >
            <span className="flex items-center justify-center gap-2">
              <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              Talk to Kalm Now
            </span>
          </a>

          <div className="mt-5 sm:mt-6 pt-5 sm:pt-6 border-t border-[#284203]/10 text-center">
            <p className="text-xs sm:text-sm text-[#284203]/60 mb-2 sm:mb-3">
              Already using Kalm?
            </p>
            <a
              href="https://t.me/Kalm_ai_bot"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#284203] hover:underline text-xs sm:text-sm font-medium"
            >
              Open Telegram Bot
            </a>
          </div>
        </div>

        <p className="text-center text-[#284203]/60 text-xs sm:text-sm mt-5 sm:mt-6">
          You are not alone. Help is always available.
        </p>
      </div>
    </main>
  )
}
