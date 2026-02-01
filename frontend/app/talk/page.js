'use client'

import { useConversation } from '@11labs/react'
import { useState, useCallback } from 'react'

export default function TalkPage() {
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState(null)

  const conversation = useConversation({
    onConnect: () => {
      console.log('Connected to ElevenLabs')
      setIsConnecting(false)
    },
    onDisconnect: () => {
      console.log('Disconnected from ElevenLabs')
    },
    onError: (error) => {
      console.error('Conversation error:', error)
      setError('Connection error. Please try again.')
      setIsConnecting(false)
    },
    onMessage: (message) => {
      console.log('Message:', message)
    },
  })

  const startConversation = useCallback(async () => {
    setIsConnecting(true)
    setError(null)

    try {
      // Request microphone permission
      await navigator.mediaDevices.getUserMedia({ audio: true })

      // Get signed URL from backend
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await fetch(`${apiUrl}/api/conversation/start`, {
        method: 'POST',
      })

      if (!res.ok) {
        throw new Error('Failed to get conversation URL')
      }

      const data = await res.json()

      // Start the conversation session
      await conversation.startSession({
        signedUrl: data.signed_url,
      })
    } catch (err) {
      console.error('Failed to start conversation:', err)
      setError(err.message || 'Failed to start conversation')
      setIsConnecting(false)
    }
  }, [conversation])

  const endConversation = useCallback(async () => {
    await conversation.endSession()
  }, [conversation])

  const getStatusColor = () => {
    switch (conversation.status) {
      case 'connected':
        return 'bg-[#284203]'
      case 'connecting':
        return 'bg-[#284203]/60'
      default:
        return 'bg-[#284203]/30'
    }
  }

  const getStatusText = () => {
    if (isConnecting) return 'Connecting...'
    switch (conversation.status) {
      case 'connected':
        return conversation.isSpeaking ? 'Kalm is speaking...' : 'Listening...'
      default:
        return 'Not connected'
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4 sm:p-6 md:p-8">
      <div className="w-full max-w-[28rem]">
        <div className="text-center mb-6 sm:mb-8">
          <h1 className="text-4xl sm:text-5xl font-semibold text-[#284203] mb-2">Talk to Kalm</h1>
          <p className="text-[#284203]/80 text-base sm:text-lg italic">
            Real-time voice support
          </p>
        </div>

        <div className="bg-[#d9e4bf] backdrop-blur-sm rounded-2xl shadow-xl p-6 sm:p-8">
          {/* Status Indicator */}
          <div className="flex items-center justify-center gap-2 sm:gap-3 mb-6 sm:mb-8">
            <div className={`w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full ${getStatusColor()} ${conversation.status === 'connected' ? 'animate-pulse' : ''}`} />
            <span className="text-[#284203]/80 text-sm sm:text-base">{getStatusText()}</span>
          </div>

          {/* Visual Feedback */}
          {conversation.status === 'connected' && (
            <div className="flex justify-center mb-6 sm:mb-8">
              <div className={`w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-[#7d9f6f] flex items-center justify-center ${conversation.isSpeaking ? 'animate-pulse' : ''}`}>
                <svg
                  className="w-10 h-10 sm:w-12 sm:h-12 text-[#284203]/80"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  {conversation.isSpeaking ? (
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15.536a5 5 0 001.414 1.414m2.828-9.9a9 9 0 012.828-2.828"
                    />
                  ) : (
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                    />
                  )}
                </svg>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-5 sm:mb-6 p-3 sm:p-4 bg-red-50 text-red-700 rounded-lg text-center text-sm sm:text-base">
              {error}
            </div>
          )}

          {/* Action Buttons */}
          {conversation.status !== 'connected' ? (
            <button
              onClick={startConversation}
              disabled={isConnecting}
              className="w-full py-3 sm:py-4 px-4 bg-[#7d9f6f] text-[#284203]/80 font-semibold rounded-lg hover:bg-[#6d8f5f] transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
            >
              {isConnecting ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4 sm:h-5 sm:w-5" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Connecting...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  Start Conversation
                </span>
              )}
            </button>
          ) : (
            <button
              onClick={endConversation}
              className="w-full py-3 sm:py-4 px-4 bg-red-500 text-white font-semibold rounded-lg hover:bg-red-600 transition-colors text-sm sm:text-base"
            >
              <span className="flex items-center justify-center gap-2">
                <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                End Conversation
              </span>
            </button>
          )}

          <p className="text-center text-[#284203]/60 text-xs sm:text-sm mt-5 sm:mt-6">
            Speak freely - Kalm is here to listen and support you.
          </p>
        </div>

        <div className="text-center mt-5 sm:mt-6">
          <a
            href="/"
            className="text-[#284203]/60 hover:text-[#284203] text-xs sm:text-sm"
          >
            ← Back to home
          </a>
        </div>
      </div>
    </main>
  )
}
