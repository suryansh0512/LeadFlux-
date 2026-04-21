# Sample Conversations

Three complete sample conversations demonstrating the agent's capabilities.

---

## Conversation 1: Product Discovery → Lead Capture

> Shows the full funnel: greeting → product questions → sign-up → lead capture.

```
You: Hi!

AutoStream Agent: Hey there! 👋 Welcome! I'm the AutoStream assistant.
I'd love to help you learn about our automated video editing tools. What
would you like to know?

You: What plans do you have?

AutoStream Agent: We offer two plans:

📌 **Basic Plan** — $29/month
  • 10 videos per month
  • 720p export quality
  • Basic auto-editing tools
  • Standard templates library
  • Email support (business hours)
  Best for hobbyist creators getting started.

🚀 **Pro Plan** — $79/month
  • Unlimited videos per month
  • 4K export quality
  • AI-powered captions and subtitles
  • Advanced auto-editing with AI scene detection
  • Premium templates library
  • Priority rendering queue
  • 24/7 dedicated support
  Best for professional creators and agencies.

Would you like to know more about either plan?

You: The Pro plan looks perfect. I want to sign up!

AutoStream Agent: That's awesome! 🎉 I'd love to get you started with
the Pro plan. Could you tell me your full name?

You: Sure, I'm Priya Sharma

AutoStream Agent: Great to meet you, Priya! 😊 Could you share your
email address so we can set up your account?

You: priya@streamstudio.com

AutoStream Agent: Perfect! One last thing — what's your primary content
creation platform? (e.g., YouTube, TikTok, Instagram)

You: I create content on Instagram and TikTok mainly

==================================================
  🎯 LEAD CAPTURED SUCCESSFULLY
==================================================
  Name:     Priya Sharma
  Email:    priya@streamstudio.com
  Platform: Instagram, TikTok
==================================================

AutoStream Agent: You're all set, Priya! 🎬 I've captured your
information and our team will reach out shortly to get you started
with the Pro plan. Welcome to AutoStream!
```

---

## Conversation 2: Policy Questions Only (No Lead Capture)

> Shows that the tool is NOT triggered when the user only asks questions.

```
You: Hello

AutoStream Agent: Hi there! 👋 How can I help you today? I'm here to
answer any questions about AutoStream's video editing tools.

You: What's your refund policy?

AutoStream Agent: Great question! We offer a full refund within the
first 7 days of your subscription. After that 7-day window, refunds
are not available. So you can essentially try us risk-free for the
first week!

You: What if I want to cancel?

AutoStream Agent: You can cancel your subscription at any time! Your
access will continue until the end of your current billing period, so
you'll get the full value of what you've already paid for.

You: Do you offer a free trial?

AutoStream Agent: We don't currently offer a free trial, but our 7-day
refund policy means you can try AutoStream risk-free. If it's not the
right fit within that first week, you'll get a full refund.

You: Okay thanks, I'll think about it

AutoStream Agent: Of course! Take your time. When you're ready, I'm
here to help you get started. Have a great day! 😊

You: bye

AutoStream Agent: Thanks for chatting! Have a great day! 🎬✨
```

**Note**: `mock_lead_capture()` was never called — the user stayed in the
product inquiry flow and never expressed sign-up intent.

---

## Conversation 3: Direct Sign-Up (Minimal Turns)

> Shows a user who jumps straight to high intent with info already provided.

```
You: I want to subscribe to AutoStream. My name is Alex Chen and my
email is alex@vloglife.com. I'm a YouTuber.

==================================================
  🎯 LEAD CAPTURED SUCCESSFULLY
==================================================
  Name:     Alex Chen
  Email:    alex@vloglife.com
  Platform: YouTube
==================================================

AutoStream Agent: Welcome aboard, Alex! 🎉 I've captured all your
details — name, email, and your YouTube platform. Our team will be in
touch shortly to set up your AutoStream account. Thanks for choosing
us, and happy creating! 🎬

You: Thanks!

AutoStream Agent: You're welcome, Alex! We're excited to have you.
If you ever have questions, don't hesitate to reach out. Happy editing! ✨
```

**Note**: The agent extracted all 3 fields from a single message and
fired `mock_lead_capture()` immediately — no unnecessary follow-up
questions needed.
