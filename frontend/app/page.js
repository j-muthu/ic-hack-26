import SubmitForm from '../components/SubmitForm'

export default function Home() {
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
            Get Support Now
          </h2>
          <p className="text-gray-600 mb-6">
            Receive a personalized supportive voice message via Telegram.
          </p>

          <SubmitForm />
        </div>

        <p className="text-center text-white/60 text-sm mt-6">
          You are not alone. Help is always available.
        </p>
      </div>
    </main>
  )
}
