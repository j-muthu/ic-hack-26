I am at a hackathon where there's a track for social good. Here's the description:

At IMC, we believe that opportunity and education can change lives. Through the IMC Charitable Foundation, we support initiatives that help young people fulfil their potential, and we invite you to do the same.
In this challenge, teams will be asked to design and build a technology-driven solution for a charitable organization of your choice, addressing a real-world problem faced by that organization or its beneficiaries.
You may choose any eligible charity, or work with inspiration from IMC’s existing charity partnerships. The goal is simple: use technology to create meaningful, positive social impact.

The scoring is as follows:
Category, Grade range
Technical solution, 1-10
Impact (reach + depth), 1-10

The charitable organisation has to be aligned with supporting youth, education, inclusion or opportunity. 

There is also a "best use of elevenlabs prize" - Build a project that uses ElevenLabs, an AI audio platform that generates natural and expressive speech.

I want to create a web app that helps recovering addicts. I want to use Elevenlabs voice AI to provide support: 24/7 therapy, affirmations, and potential intervention.

Features:
- 24/7 Elevenlabs therapist
- Talk to your "future self" by using elevenlabs voice cloning
- Provides daily affirmations using elevenlabs to generate a voice note that's then sent using the telegram bot api voice note function
- Daily tracker and journalling
- App syncs with your calendar so that when you go to social events, it can connect to an elevenlabs voice agent to generate a voice note, then send a telegram voice note or call you to provide you with support (e.g. to stop a recovering alcoholic from feeling pressured to drink at a work social).

We want to create a web app using the following tech stack:
- frontend: react/next.js for vercel deployment
- python fastapi for the backend
- connect to telegram api bot https://core.telegram.org/bots/api#sendvoice
- supabase database if necessary
- elevenlabs for all voice technology
 

Provide a plan for this project. The above is just a guideline, not necessarily set in stone.

