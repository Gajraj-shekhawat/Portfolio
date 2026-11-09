"""Builds the service landing pages (one folder + index.html each) and refreshes sitemap.xml.

Run from the repo root:  python3 tools/build_pages.py
Edit the PAGES list below to change copy; never hand-edit the generated HTML.
"""
import datetime
import hashlib
import html
import re
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "tools"))
from cases import CASES  # noqa: E402
from posts import POSTS as ALL_POSTS  # noqa: E402
SITE = "https://gajrajshekhawat.com"
TODAY = datetime.date.today().isoformat()
NOW_ISO = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).replace(microsecond=0).isoformat()
GH_REDIRECT = '<script>if(location.hostname.endsWith("github.io")){location.replace("https://gajrajshekhawat.com"+location.pathname.replace(/^\\/Portfolio/,"")+location.search+location.hash)}</script>'
EMAIL = "contact@gajrajshekhawat.com"
PHONE = "+91 94145 84444"
PHONE_E164 = "+919414584444"
CASES_PUBLISHED = "2026-11-08"  # when the case studies first went live
LASTMOD_FILE = ROOT / "tools" / "lastmod.json"  # real last-content-change date per URL (sitemap + dateModified)

# Posts publish themselves on their date: only posts dated today or earlier are built.
# (.github/workflows/publish-posts.yml rebuilds daily when a post falls due.)
POSTS = sorted([p for p in ALL_POSTS if p["date"] <= TODAY], key=lambda p: p["date"], reverse=True)
WA = "https://wa.me/919414584444?text=Hi%20Gajraj%2C%20I%27d%20like%20to%20discuss%20a%20project."

PROOF = {
    "equiti": ("Equiti · global trading platform", "Engineering for Equiti Group's multi-asset trading platform, at Shuru Technologies.", "https://www.equiti.com"),
    "pickup": ("Pickup Coffee · 500+ stores", "Data platform (Airflow, BigQuery, Metabase) and backends for the customer app, barista tablet app and back office. 30% lower API latency.", "https://pickup-coffee.com"),
    "nks": ("Neem Karoli Sales · ordering platform", "Two Android apps, web admin and API for a wholesaler, built solo: OTP sign-in, Cashfree payments, GST invoices, 1,290+ tests.", "https://neemkarolisales.in"),
    "competishun": ("Competishun · JEE/NEET coaching", "Backend of an online learning platform used by thousands of students at once: live classes, tests, payments.", "https://competishun.com"),
    "yugam_web": ("Yugam International School · website", "Next.js school website with paid event passes, OTP sign-in, Cashfree payments and SEO.", "https://yugam.co"),
    "yugam_ask": ("Yugam Ask · AI agent", "Plain-English questions over 1.7M schools: text-to-SQL on a self-hosted LLM, with a GPU that starts on demand.", None),
    "yugam_ai": ("Yugam AI · lesson planner & call summaries", "AI tools for teachers and admissions, including Indian-language call transcription, on the school's own server.", "https://ai.yugam.co"),
    "face": ("Face attendance", "A class marked present from one photo, using OpenCV on an ordinary CPU, with no cloud AI.", None),
    "streamfit": ("StreamFit · Shikhar Classes", "Adaptive aptitude test and career-stream recommender with AI-read OMR sheets and PDF reports.", "https://streamfit.shikharedtech.com"),
    "shikhar": ("Shikhar EdTech · complete coaching platform", "Website with SEO, online JEE/NEET test platform, admissions CRM, JoSAA college predictors and Razorpay admissions, all built and run by me.", "https://shikharedtech.com"),
    "gram": ("Gram Sansad · village websites", "A platform that gives every village its own website, all managed from one system.", "https://gramsansad.com"),
}

PAGES = [
    {
        "slug": "about",
        "nav": "About Gajraj",
        "title": "About Gajraj Singh Shekhawat · Software Engineer, Jaipur",
        "description": "Gajraj Singh Shekhawat (Gajraj Shekhawat) is a full-stack software engineer from Jaipur, India, at Shuru Technologies, building apps, backends and AI.",
        "eyebrow": "About Gajraj Shekhawat",
        "h1": 'Gajraj Singh Shekhawat, <em>software engineer</em> from Jaipur',
        "lead": "I'm Gajraj Singh Shekhawat (Gajraj Shekhawat), a full-stack software engineer based in Jaipur, Rajasthan. I work at Shuru Technologies on Equiti's global trading platform, and earlier built Pickup Coffee's data platform and app backends and Competishun's learning platform. Alongside that, I lead a small team building websites, apps, e-commerce and AI tools for schools and businesses.",
        "what": [
            ("Software engineer at Shuru Technologies", "Backend and full-stack work on Equiti's multi-asset trading platform, and earlier on Pickup Coffee's data platform and Node.js microservices with Maya, GCash and card payments."),
            ("Full-stack developer at AFM Bigtech", "Backend for Competishun, an online JEE/NEET learning platform used by thousands of students at once: live classes, tests and payments."),
            ("Software consultant and tech advisor", "Complete products for a CBSE school, a JEE/NEET coaching institute and a beverage wholesaler: websites, apps, payments, CRMs and private AI."),
            ("Where to find me", "Jaipur, India, working remotely with teams worldwide. Profiles: LinkedIn (gajrajshekhawat), GitHub (Gajraj-shekhawat), Upwork, Peerlist and X."),
        ],
        "proof": ["equiti", "pickup", "yugam_ask", "shikhar"],
        "stack": ["Node.js", "TypeScript", "Python", "React", "Next.js", "React Native", "PostgreSQL", "MySQL", "MongoDB", "Redis", "AWS", "GCP"],
        "faqs": [
            ("Who is Gajraj Singh Shekhawat?", "Gajraj Singh Shekhawat, also written Gajraj Shekhawat, is a full-stack software engineer from Jaipur, Rajasthan, India. He works at Shuru Technologies on Equiti's trading platform and builds websites, apps and AI for businesses."),
            ("What does Gajraj Shekhawat work on?", "Backends and APIs (Node.js, TypeScript, Python), web and mobile apps (React, Next.js, React Native), e-commerce and payments, and AI features such as chatbots and text-to-SQL agents."),
            ("Where is Gajraj Shekhawat based?", "Jaipur, Rajasthan, India. He works remotely with clients and teams worldwide."),
            ("How can I contact Gajraj Shekhawat?", "Email contact@gajrajshekhawat.com, use the contact form on this site, or message on WhatsApp at +91 94145 84444."),
        ],
    },
    {
        "slug": "hire-software-engineer",
        "nav": "Hire a software engineer",
        "title": "Hire a Remote Software Engineer · Gajraj Singh Shekhawat",
        "description": "Hire Gajraj Singh Shekhawat, a remote full-stack software engineer with production work for Equiti, Pickup Coffee and Competishun: web, mobile, APIs and AI.",
        "eyebrow": "Hire a software engineer",
        "h1": 'Hire a remote software engineer who <em>ships to production</em>',
        "lead": "I'm Gajraj Singh Shekhawat, a full-stack software engineer (frontend, backend, mobile, AI and data) at Shuru Technologies, working on Equiti's trading platform. For startups, schools and businesses, I take on select projects end to end: planning, backend, web and mobile apps, payments, AI and deployment.",
        "what": [
            ("New products, from idea to launch", "MVPs and full products: scope, architecture, backend, web and Android apps, admin panels, payments and launch."),
            ("Extra engineering capacity", "Join your team remotely on a feature, an integration or a performance problem, or bring my own small team of developers for larger builds, with me as the single accountable lead."),
            ("Rescue and improvement", "Slow APIs, flaky deployments, missing tests, or a codebase someone else left behind. I find what's wrong and fix it."),
            ("Long-term technology partner", "Like I do for a CBSE school: ongoing development, a small team to lead, and someone accountable for the tech."),
        ],
        "proof": ["equiti", "pickup", "shikhar", "nks"],
        "stack": ["Node.js", "TypeScript", "Python", "React", "Next.js", "React Native", "PostgreSQL", "MongoDB", "Redis", "AWS", "GCP", "Docker"],
        "faqs": [
            ("How do I hire Gajraj?", "Send a message through the contact form, email or WhatsApp with a short description of what you need. You'll get a reply within a day and a short call to discuss scope."),
            ("Does he work with international clients?", "Yes. He works remotely with teams worldwide, including the Philippines, Mexico, the UAE and the UK, from India (IST, UTC+5:30) with working hours that overlap Europe, the Middle East and Asia."),
            ("How is pricing decided?", "After a short call you get a clear scope, timeline and fixed quote before any work begins. Ongoing work can also be monthly."),
            ("What experience does he have?", "Production software for global companies: Equiti's trading platform and Pickup Coffee's data platform and apps at Shuru Technologies, Competishun's learning platform at AFM Bigtech, and complete products for schools and businesses."),
        ],
    },
    {
        "slug": "backend-developer",
        "nav": "Backend developer",
        "title": "Backend Developer · Node.js, Python, APIs · Gajraj Shekhawat",
        "description": "Backend developer for APIs, microservices, databases and data pipelines in Node.js and Python. Cut API latency 30% on a 500-store coffee chain's apps.",
        "eyebrow": "Backend development",
        "h1": 'Backend developer for APIs that stay <em>fast under load</em>',
        "lead": "I design and build the backend that apps depend on: APIs, microservices, databases, queues, data pipelines and the monitoring that keeps them healthy. I've cut API latency by 30% and database load by 40% on a coffee chain's high-traffic apps.",
        "what": [
            ("APIs & microservices", "REST APIs and services in Node.js (Express, Fastify, NestJS) or Python (FastAPI), with authentication, rate limits and tests."),
            ("Databases & performance", "PostgreSQL, MySQL and MongoDB schema design, indexing and query tuning, plus Redis caching when speed matters."),
            ("Queues, jobs & integrations", "Background jobs with BullMQ/Redis, payment gateways (Razorpay, Cashfree), WhatsApp and SMS OTP, GST invoices, webhooks."),
            ("Data pipelines & dashboards", "Apache Airflow pipelines into BigQuery and Metabase dashboards, so your team can finally see its numbers."),
        ],
        "proof": ["pickup", "equiti", "competishun", "nks"],
        "stack": ["Node.js", "Express", "Fastify", "NestJS", "Python", "FastAPI", "PostgreSQL", "MongoDB", "Redis", "BullMQ", "Airflow", "BigQuery", "OpenTelemetry", "Kubernetes"],
        "faqs": [
            ("Which backend languages does Gajraj use?", "Mainly Node.js/TypeScript (Express, Fastify, NestJS) and Python (FastAPI), with PostgreSQL, MongoDB, MySQL and Redis."),
            ("Can he make a slow API faster?", "Yes. On Pickup Coffee's apps he cut API latency by 30% and database load by 40% with query tuning, indexing and Redis caching, and set up tracing to find bottlenecks."),
            ("Can he build data pipelines and dashboards?", "Yes. He built Pickup Coffee's data platform: Airflow pipelines from Google Cloud Storage into BigQuery and Metabase dashboards for the marketing team."),
        ],
    },
    {
        "slug": "full-stack-developer",
        "nav": "Full-stack developer",
        "title": "Full-Stack Developer · Web & Mobile Apps · Gajraj Shekhawat",
        "description": "Full-stack developer for web and Android apps with React, Next.js, React Native and Node.js: customer apps, admin panels and ordering systems, end to end.",
        "eyebrow": "Full-stack development",
        "h1": 'Full-stack developer for <em>web & mobile apps</em>',
        "lead": "One developer for the whole product: the app your customers use, the admin panel your team runs, and the backend in between. I recently built a wholesaler's two Android apps, web admin and API on my own.",
        "what": [
            ("Customer apps", "Android apps with React Native/Expo and fast web apps with React and Next.js, including OTP sign-in and payments."),
            ("Admin panels & dashboards", "Internal tools your team will actually use: orders, inventory, users, reports and roles."),
            ("Ordering & booking systems", "Carts, pricing rules, order tracking, delivery roles, invoices and notifications."),
            ("Updates without the Play Store", "Self-updating Android apps with forced updates and safe rollbacks, as built for Neem Karoli Sales."),
        ],
        "proof": ["nks", "shikhar", "pickup", "yugam_web"],
        "stack": ["React", "Next.js", "TypeScript", "React Native", "Expo", "Tailwind", "Node.js", "Fastify", "MongoDB", "PostgreSQL"],
        "faqs": [
            ("Can Gajraj build both the app and the backend?", "Yes. For Neem Karoli Sales he designed and built two Android apps, a web admin and the API on his own, with payments, GST invoices and 1,290+ automated tests."),
            ("Does he build Android and iOS apps?", "He builds cross-platform apps with React Native and Expo. His recent production apps are Android; iOS uses the same codebase."),
            ("Which frontend frameworks does he use?", "React and Next.js for the web, React Native for mobile, with TypeScript and Tailwind CSS."),
        ],
    },
    {
        "slug": "website-development",
        "nav": "Website development",
        "title": "Website Development for Businesses · Gajraj Shekhawat",
        "description": "Fast, SEO-ready websites for businesses, schools, coaching institutes and startups, with online payments, WhatsApp buttons and forms that bring enquiries.",
        "eyebrow": "Website development",
        "h1": 'Websites that load fast, rank well and <em>bring enquiries</em>',
        "lead": "I build websites for businesses, schools and startups that do more than look good: they load in about a second, show up on Google and AI search, take payments and turn visitors into enquiries.",
        "what": [
            ("Business & personal websites", "Modern, mobile-first sites with your brand, services, testimonials and a contact form that lands in your inbox."),
            ("School & institute websites", "Admissions pages, disclosure pages, event passes with online payment, and an easy way to update content."),
            ("SEO & AI search setup", "Search Console, sitemaps, structured data and llms.txt so Google, ChatGPT and Perplexity understand your business."),
            ("Moving off WordPress", "Rebuild a slow WordPress site as a fast static site without breaking old links, as done for Gram Sansad."),
        ],
        "proof": ["shikhar", "yugam_web", "gram", "nks"],
        "stack": ["Next.js", "React", "Tailwind", "Cloudflare", "SEO", "Cashfree", "Razorpay", "Google Search Console"],
        "faqs": [
            ("How long does a website take?", "A typical business website takes one to three weeks depending on pages and features. You get a live preview link from the first week."),
            ("Will the website show up on Google?", "Every site is set up for search: fast loading, structured data, sitemap and Google Search Console, plus llms.txt for AI assistants."),
            ("Can the website accept payments?", "Yes, through Razorpay or Cashfree, with OTP sign-in when needed, as on the Yugam International School website."),
        ],
    },
    {
        "slug": "business-website-jaipur",
        "nav": "Business website in 7 days",
        "title": "Business Website in 7 Days · Jaipur & India · Gajraj Shekhawat",
        "description": "A fast, mobile-friendly website for your shop, clinic, coaching centre or restaurant in Jaipur and India, with WhatsApp button and Google listing, in ~7 days.",
        "eyebrow": "Business website · Jaipur & India",
        "h1": 'Your business online in <em>7 days</em>',
        "lead": "Customers search on Google and WhatsApp before they visit. I build a fast, mobile-friendly website for your shop, clinic, coaching centre or restaurant, with a WhatsApp button, your Google listing set up and a simple enquiry form, usually ready in about a week. Packages start at ₹14,999.",
        "what": [
            ("Website that works on every phone", "Clean, fast pages with your services, photos, prices, location map and timings, easy for customers to read on a mobile."),
            ("WhatsApp & call buttons", "One tap to chat on WhatsApp or call you, so enquiries come straight to your phone."),
            ("Show up on Google", "Google Business listing, search setup and the basics that help nearby customers find you."),
            ("Enquiries, bookings & payments", "Enquiry forms that land in your WhatsApp or email, plus online booking or payments (Razorpay, Cashfree) when you need them."),
        ],
        "proof": ["yugam_web", "shikhar", "nks", "gram"],
        "stack": ["Next.js", "React", "Tailwind", "WhatsApp", "Google Business Profile", "Razorpay", "Cashfree", "SEO"],
        "faqs": [
            ("How long does a business website take?", "Most small business websites are ready in about 7 days once you share your content and photos. Bigger sites with bookings or payments take 2–3 weeks."),
            ("What do I need to give you?", "Your business name, services, photos, timings, address and phone/WhatsApp number. I help write the text if you don't have it."),
            ("Will customers find me on Google?", "Yes. Every site comes with search setup and help with your Google Business listing so nearby customers can find you on Search and Maps."),
            ("Can I update the website myself later?", "Yes, simple changes are easy, and I offer ongoing support if you'd rather I handle updates."),
            ("How much does a business website cost?", "Packages start at ₹14,999 for a website of up to 5 pages: mobile-friendly design, WhatsApp and call buttons, an enquiry form, Google Business Profile setup, basic SEO, free SSL and hosting setup, and one month of support. Your domain is billed at cost (usually under ₹1,500 a year). Online booking, payments or more pages are quoted separately."),
            ("How do I get a price?", "Send a WhatsApp message with what your business does. You'll get a clear fixed quote, usually within a day."),
        ],
    },
    {
        "slug": "ecommerce-development",
        "nav": "E-commerce development",
        "title": "E-commerce Website & App Development · Gajraj Shekhawat",
        "description": "E-commerce development for retail, wholesale and D2C: online stores, B2B ordering apps, payments, offers, inventory, GST invoicing and delivery tracking.",
        "eyebrow": "E-commerce development",
        "h1": 'Online stores and ordering apps that <em>sell more</em>',
        "lead": "I build e-commerce that fits how you actually sell: an online store for retail customers, a B2B portal where shops reorder in bulk, or a mobile app for your regular buyers. Catalogue, cart, payments, invoices and delivery, all connected to one backend you own.",
        "what": [
            ("Online stores (B2C & D2C)", "Product catalogue, search and filters, cart and checkout, coupons, customer accounts and order tracking, on a fast, SEO-ready website."),
            ("B2B & wholesale ordering", "Apps and portals where retailers and distributors order in bulk, with server-side pricing, GST invoices and delivery tracking, as built for a beverage wholesaler."),
            ("Payments, offers & loyalty", "Razorpay and Cashfree checkout, wallets, vouchers, referral programs and loyalty rewards, as on Pickup Coffee's ordering apps."),
            ("Inventory, orders & admin", "Stock, order and delivery management, staff roles, reports and dashboards, plus WhatsApp and SMS updates for customers."),
        ],
        "proof": ["nks", "pickup", "yugam_web", "shikhar"],
        "stack": ["Next.js", "React", "React Native", "Node.js", "MongoDB", "PostgreSQL", "Redis", "Razorpay", "Cashfree", "WhatsApp API", "SEO"],
        "faqs": [
            ("Can Gajraj build an e-commerce website or online store?", "Yes. He builds online stores and ordering apps end to end: catalogue, cart, checkout, payments, order tracking and an admin panel, for retail, wholesale and D2C businesses."),
            ("Can he build a B2B or wholesale ordering app?", "Yes. For Neem Karoli Sales, a beverage wholesaler, he built Android apps for retailers and delivery staff, a web admin and the API, with online payments and GST invoices."),
            ("Should I use Shopify or a custom store?", "If a ready-made platform like Shopify fits your needs, he will tell you. A custom build makes sense for B2B ordering, special pricing rules, your own mobile app or deep integrations with your other systems."),
            ("Which payment gateways does he integrate?", "Razorpay and Cashfree in production, plus wallets, vouchers and referral rewards from his work on Pickup Coffee's apps."),
        ],
    },
    {
        "slug": "ai-developer",
        "nav": "AI developer",
        "title": "AI Developer · LLM Apps & AI Agents · Gajraj Shekhawat",
        "description": "AI developer for LLM apps, AI agents, text-to-SQL, document reading, transcription and computer vision, with self-hosted models when privacy or cost matters.",
        "eyebrow": "AI development",
        "h1": 'AI features that <em>actually get used</em>',
        "lead": "I add AI where it saves real time: agents that answer questions over your data, document and answer-sheet reading, call transcription and summaries, and computer vision. When privacy or cost matters, models run on your own server.",
        "what": [
            ("Chat over your own data", "An AI agent that turns plain-English questions into safe, read-only SQL, like Yugam Ask over 1.7 million schools."),
            ("Documents & OMR sheets", "Reading forms, invoices and exam answer sheets with AI, with checks so results can be trusted."),
            ("Speech & summaries", "Call transcription and summaries in Indian languages for sales and admissions teams."),
            ("Computer vision", "Face recognition attendance from a single photo, running on an ordinary CPU with no cloud AI."),
        ],
        "proof": ["yugam_ask", "yugam_ai", "face", "streamfit"],
        "stack": ["LLM agents", "Text-to-SQL", "vLLM", "Ollama", "Gemini", "OpenCV", "FastAPI", "Python", "PostgreSQL"],
        "faqs": [
            ("Can AI be added to an existing product?", "Yes. Most AI work is added to existing systems: a question-answering agent over your database, document reading, or summaries of calls and tickets."),
            ("Can the AI run without sending data to OpenAI or Google?", "Yes. He has deployed self-hosted models (Qwen on vLLM, Ollama) and CPU-only computer vision so sensitive data stays on your servers."),
            ("Which AI projects has Gajraj built?", "Yugam Ask (text-to-SQL agent over 1.7M schools), Yugam AI (lesson planner and Indian-language call summaries), face-recognition attendance, and AI-read OMR sheets for StreamFit."),
        ],
    },
    {
        "slug": "tech-advisor",
        "nav": "Tech advisor",
        "title": "Tech Advisor for Founders & Businesses · Gajraj Shekhawat",
        "description": "Technical advisor for founders, schools and businesses: architecture reviews, choosing the stack, build-or-buy decisions, agency code reviews and hiring.",
        "eyebrow": "Tech advisory",
        "h1": 'A trusted technical opinion <em>before you spend</em>',
        "lead": "Not every problem needs more code. As a tech advisor I help founders and leadership make the right technical calls: what to build, what to buy, who to hire, and whether the work you're paying for is any good.",
        "what": [
            ("Architecture & stack decisions", "Pick the simplest stack that will still work in two years, and avoid expensive rewrites."),
            ("Build, buy or no-code", "An honest view on when custom software is worth it and when an existing tool is better."),
            ("Agency & vendor reviews", "Review proposals, estimates and delivered code so you know what you're paying for."),
            ("Hiring & leading developers", "Write the role, run technical interviews and lead a small team, as I do for a CBSE school."),
        ],
        "proof": ["yugam_web", "nks", "pickup", "equiti"],
        "stack": ["Architecture reviews", "Code reviews", "Roadmaps", "Hiring", "Cloud costs", "Security basics"],
        "faqs": [
            ("What does a tech advisor do?", "Helps non-technical founders and leaders make technology decisions: architecture, stack, vendors, budgets and hiring, so money goes into the right things."),
            ("Can Gajraj review work done by another agency?", "Yes. He can review proposals, estimates and delivered code and give a plain-language report on quality, risks and next steps."),
            ("Is advisory available without a full project?", "Yes. Advisory can be a few calls, a one-off review, or a monthly arrangement."),
        ],
    },
]

PROCESS = [("01", "Call", "We talk through the problem and I suggest the simplest thing that solves it."),
           ("02", "Plan", "A clear scope, timeline and fixed quote. No surprises."),
           ("03", "Build", "Weekly demos on a live link, so you see progress as it happens."),
           ("04", "Launch", "Deployed, monitored, documented, and supported after launch.")]

esc = html.escape


def nav_html():
    links = "".join(f'<a href="/{p["slug"]}/">{esc(p["nav"])}</a>' for p in PAGES[:4])
    return f'''  <header class="nav" id="top">
    <div class="wrap nav__inner">
      <a href="/" class="brand" aria-label="Gajraj Shekhawat, home">
        <img class="brand__avatar" src="/images/avatar-96.webp" alt="" width="36" height="36" />
        <span class="brand__name">Gajraj Shekhawat</span>
      </a>
      <nav class="nav__links" id="navLinks" aria-label="Primary">
        <a href="/#work" data-nav>Work</a>
        <a href="/#services" data-nav>Services</a>
        <a href="/#experience" data-nav>Experience</a>
        <a href="/blog/">Blog</a>
        <a href="/#faq" data-nav>FAQ</a>
        <a href="/#contact" class="btn btn--sm btn--primary">Let's talk</a>
      </nav>
      <div class="nav__tools">
        <button class="icon-btn" id="themeToggle" type="button" aria-label="Switch light or dark theme">
          <svg class="i-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
          <svg class="i-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
        </button>
        <button class="icon-btn nav__burger" id="navToggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="navLinks">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path class="l1" d="M4 8h16"/><path class="l2" d="M4 16h16"/></svg>
        </button>
      </div>
    </div>
  </header>'''


def footer_html():
    services = "".join(f'<li><a href="/{p["slug"]}/">{esc(p["nav"])}</a></li>' for p in PAGES)
    return f'''  <footer class="footer">
    <div class="wrap">
      <nav class="footer__services" aria-label="Services">
        <p class="footer__label">Services</p>
        <ul>{services}</ul>
      </nav>
      <div class="footer__inner">
        <p>© <span id="year">2026</span> Gajraj Singh Shekhawat · Full-Stack Software Engineer &amp; Tech Advisor · Based in India, working worldwide · <a href="mailto:{EMAIL}">{EMAIL}</a> · <a href="tel:{PHONE_E164}">{PHONE}</a></p>
        <ul class="footer__links">
          <li><a href="https://www.linkedin.com/in/gajrajshekhawat/" target="_blank" rel="noopener me">LinkedIn</a></li>
          <li><a href="https://github.com/Gajraj-shekhawat" target="_blank" rel="noopener me">GitHub</a></li>
          <li><a href="https://www.upwork.com/freelancers/~015e52d28e1b27390f" target="_blank" rel="noopener me">Upwork</a></li>
          <li><a href="https://peerlist.io/gajrajshekhawat" target="_blank" rel="noopener me">Peerlist</a></li>
          <li><a href="/blog/">Blog</a></li>
          <li><a href="/assets/Gajraj-Shekhawat-Resume.pdf" target="_blank" rel="noopener">Resume</a></li>
          <li><a href="/">Home</a></li>
        </ul>
      </div>
    </div>
  </footer>'''


def page_html(p):
    url = f"{SITE}/{p['slug']}/"
    h1_text = html.unescape(p["h1"].replace("<em>", "").replace("</em>", ""))
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "@id": url + "#page", "url": url, "name": p["title"], "description": p["description"],
             "inLanguage": "en", "dateModified": NOW_ISO, "isPartOf": {"@id": SITE + "/#website"},
             "about": {"@id": SITE + "/#person"}, "breadcrumb": {"@id": url + "#breadcrumb"}},
            {"@type": "Service", "@id": url + "#service", "name": p["nav"].title() if p["slug"] != "ai-developer" else "AI Development",
             "serviceType": p["eyebrow"], "description": p["description"], "url": url,
             "provider": {"@type": "Person", "@id": SITE + "/#person", "name": "Gajraj Singh Shekhawat",
                          "url": SITE + "/", "email": EMAIL, "telephone": "+91-9414584444"},
             "areaServed": "Worldwide"},
            {"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Gajraj Singh Shekhawat", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": p["eyebrow"], "item": url}]},
            {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faqs"]]},
        ],
    }
    what = "".join(f'''          <div class="service reveal spot"{' style="--d:1"' if i % 2 else ''}>
            <h3>{esc(t)}</h3>
            <p>{esc(d)}</p>
          </div>
''' for i, (t, d) in enumerate(p["what"]))
    proof = ""
    for i, key in enumerate(p["proof"]):
        name, text, link = PROOF[key]
        a = f'\n            <a class="case__link" href="{link}" target="_blank" rel="noopener">{esc(link.split("//")[1])} <span aria-hidden="true">↗</span></a>' if link else ""
        proof += f'''          <article class="case reveal spot"{' style="--d:1"' if i % 2 else ''}>
            <h3>{esc(name)}</h3>
            <p>{esc(text)}</p>{a}
          </article>
'''
    chips = "".join(f"<li>{esc(c)}</li>" for c in p["stack"])
    process = "".join(
        '<li class="reveal"' + (f' style="--d:{i}"' if i else "") + f'><span class="process__n">{n}</span><strong>{t}</strong><p>{esc(d)}</p></li>'
        for i, (n, t, d) in enumerate(PROCESS))
    faqs = "".join(f'''          <details class="faq__item reveal"{' style="--d:1"' if i % 2 else ''}>
            <summary><h3>{esc(q)}</h3><span class="faq__icon" aria-hidden="true"></span></summary>
            <p>{esc(a)}</p>
          </details>
''' for i, (q, a) in enumerate(p["faqs"]))
    others = "".join(f'<li><a href="/{o["slug"]}/">{esc(o["nav"])} <span aria-hidden="true">→</span></a></li>' for o in PAGES if o is not p)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>{esc(p["title"])}</title>
  <meta name="description" content="{esc(p["description"])}" />
  <meta name="author" content="Gajraj Singh Shekhawat" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1" />
  <link rel="canonical" href="{url}" />
  <meta name="theme-color" content="#09090b" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Gajraj Singh Shekhawat" />
  <meta property="og:url" content="{url}" />
  <meta property="og:title" content="{esc(p["title"])}" />
  <meta property="og:description" content="{esc(p["description"])}" />
  <meta property="og:image" content="{SITE}/images/og.jpg" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="{SITE}/images/og.jpg" />
  <link rel="icon" href="/images/favicon-32.png" sizes="32x32" type="image/png" />
  <link rel="apple-touch-icon" href="/images/apple-touch-icon.png" />
  <link rel="preload" href="/fonts/geist.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/fonts/instrument-serif-italic.woff2" as="font" type="font/woff2" crossorigin />
  {GH_REDIRECT}
  <link rel="stylesheet" href="/styles.min.css" />
  <script>
    document.documentElement.classList.add('js');
    try {{ var t = localStorage.getItem('theme'); if (t) document.documentElement.dataset.theme = t; }} catch (e) {{}}
  </script>
  <script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
  </script>
</head>
<body class="subpage">
  <a class="skip" href="#main">Skip to content</a>
  <div class="progress" aria-hidden="true"><span id="progressBar"></span></div>
{nav_html()}

  <main id="main">
    <section class="hero hero--page">
      <div class="hero__bg" aria-hidden="true"><span class="blob blob--1"></span><span class="blob blob--2"></span><span class="grid"></span></div>
      <div class="wrap">
        <nav class="crumbs load" aria-label="Breadcrumb"><a href="/">Gajraj Singh Shekhawat</a> <span aria-hidden="true">/</span> <span>{esc(p["eyebrow"])}</span></nav>
        <h1 class="page-title load" style="--d:1">{p["h1"]}</h1>
        <p class="lead load" style="--d:2">{esc(p["lead"])}</p>
        <div class="hero__cta load" style="--d:3">
          <a href="/#contact" class="btn btn--primary btn--lg">Discuss your project <span class="btn__arrow" aria-hidden="true">→</span></a>
          <a href="{WA}" class="btn btn--ghost btn--lg" target="_blank" rel="noopener">WhatsApp {PHONE}</a>
          <a href="mailto:{EMAIL}" class="btn btn--link">{EMAIL}</a>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <header class="section__head reveal">
          <p class="eyebrow"><span>01</span> What I do</p>
          <h2>How I can help</h2>
        </header>
        <div class="services services--2">
{what}        </div>
        <ul class="chips page-chips reveal" aria-label="Technologies">{chips}</ul>
      </div>
    </section>

    <section class="section section--alt">
      <div class="wrap">
        <header class="section__head reveal">
          <p class="eyebrow"><span>02</span> Proof</p>
          <h2>Recent work in <em>production</em></h2>
          <p class="section__sub">Real products for real organisations. <a href="/#work">See all work →</a></p>
        </header>
        <div class="cases">
{proof}        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <header class="section__head reveal">
          <p class="eyebrow"><span>03</span> Process</p>
          <h2>How we'll work together</h2>
        </header>
        <ol class="process">{process}</ol>
      </div>
    </section>

    <section class="section section--alt" id="faq">
      <div class="wrap faq">
        <header class="section__head reveal">
          <p class="eyebrow"><span>04</span> FAQ</p>
          <h2>Common <em>questions</em></h2>
        </header>
        <div class="faq__list">
{faqs}        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="cta-band reveal">
          <h2>Let's talk about <em>your project</em></h2>
          <p class="section__sub">Tell me what you need. I usually reply within a day.</p>
          <div class="hero__cta">
            <a href="/#contact" class="btn btn--primary btn--lg">Send a message <span class="btn__arrow" aria-hidden="true">→</span></a>
            <a href="{WA}" class="btn btn--ghost btn--lg" target="_blank" rel="noopener">WhatsApp</a>
            <a href="tel:{PHONE_E164}" class="btn btn--ghost btn--lg">{PHONE}</a>
          </div>
        </div>
        <nav class="other-services reveal" aria-label="Other services">
          <p class="footer__label">Other services</p>
          <ul>{others}</ul>
        </nav>
      </div>
    </section>
  </main>

{footer_html()}

  <a href="#top" class="totop" id="toTop" aria-label="Back to top">
    <svg viewBox="0 0 48 48" aria-hidden="true"><circle class="totop__track" cx="24" cy="24" r="21" /><circle class="totop__bar" cx="24" cy="24" r="21" /></svg>
    <span aria-hidden="true">↑</span>
  </a>
  <div class="cursor" aria-hidden="true"><span class="cursor__dot"></span><span class="cursor__ring"></span></div>
  <script src="/script.js" defer></script>
</body>
</html>
'''


def case_html(c):
    url = f"{SITE}/work/{c['slug']}/"
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Article", "@id": url + "#article", "headline": c["title"][:110], "description": c["description"], "url": url,
             "image": f"{SITE}/images/og.jpg", "datePublished": CASES_PUBLISHED, "dateModified": NOW_ISO, "inLanguage": "en",
             "author": {"@type": "Person", "@id": SITE + "/#person", "name": "Gajraj Singh Shekhawat", "url": SITE + "/"},
             "publisher": {"@type": "Person", "@id": SITE + "/#person", "name": "Gajraj Singh Shekhawat"},
             "about": c["name"], "keywords": ", ".join(c["stack"])},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Gajraj Singh Shekhawat", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Work", "item": SITE + "/#work"},
                {"@type": "ListItem", "position": 3, "name": c["name"], "item": url}]},
        ],
    }
    facts = "".join(f'<div class="stat"><dt>{esc(k)}</dt><dd class="fact">{esc(v)}</dd></div>' for k, v in c["facts"])
    sol = "".join(f"<li>{esc(x)}</li>" for x in c["solution"])
    res = "".join(f"<li>{esc(x)}</li>" for x in c["results"])
    chips = "".join(f"<li>{esc(x)}</li>" for x in c["stack"])
    visit = (f'<a class="btn btn--ghost btn--lg" href="{c["url"]}" target="_blank" rel="noopener">Visit {esc(c["url"].split("//")[1])} ↗</a>'
             if c["url"] else "")
    more = "".join(f'<li><a href="/work/{o["slug"]}/">{esc(o["name"])} <span aria-hidden="true">→</span></a></li>' for o in CASES if o is not c)
    body = f'''    <section class="hero hero--page">
      <div class="hero__bg" aria-hidden="true"><span class="blob blob--1"></span><span class="blob blob--2"></span><span class="grid"></span></div>
      <div class="wrap">
        <nav class="crumbs load" aria-label="Breadcrumb"><a href="/">Gajraj Singh Shekhawat</a> <span aria-hidden="true">/</span> <a href="/#work">Work</a> <span aria-hidden="true">/</span> <span>{esc(c["name"])}</span></nav>
        <p class="eyebrow load" style="--d:1">{esc(c["eyebrow"])}</p>
        <h1 class="page-title load" style="--d:2">{c["h1"]}</h1>
        <p class="lead load" style="--d:3">{esc(c["summary"])}</p>
        <div class="hero__cta load" style="--d:4">
          <a href="/#contact" class="btn btn--primary btn--lg">Build something similar <span class="btn__arrow" aria-hidden="true">→</span></a>
          {visit}
        </div>
        <dl class="stats facts load" style="--d:5">{facts}</dl>
      </div>
    </section>

    <section class="section">
      <div class="wrap prose">
        <div class="reveal"><p class="eyebrow"><span>01</span> The challenge</p><p class="prose__lead">{esc(c["challenge"])}</p></div>
        <div class="reveal"><p class="eyebrow"><span>02</span> What I built</p><ul class="prose__list">{sol}</ul></div>
        <div class="reveal"><p class="eyebrow"><span>03</span> Results</p><ul class="prose__list prose__list--results">{res}</ul></div>
        <div class="reveal"><p class="eyebrow"><span>04</span> Stack</p><ul class="chips page-chips">{chips}</ul></div>
      </div>
    </section>

    <section class="section section--alt">
      <div class="wrap">
        <div class="cta-band reveal">
          <h2>Want something like this <em>for your business?</em></h2>
          <p class="section__sub">Tell me what you need. I usually reply within a day.</p>
          <div class="hero__cta">
            <a href="/#contact" class="btn btn--primary btn--lg">Send a message <span class="btn__arrow" aria-hidden="true">→</span></a>
            <a href="{WA}" class="btn btn--ghost btn--lg" target="_blank" rel="noopener">WhatsApp {PHONE}</a>
          </div>
        </div>
        <nav class="other-services reveal" aria-label="More case studies">
          <p class="footer__label">More case studies</p>
          <ul>{more}</ul>
        </nav>
      </div>
    </section>'''
    return shell(c["title"], c["description"], url, ld, body, "article")


def fmt_date(d):
    return datetime.date.fromisoformat(d).strftime("%-d %b %Y")


def unlink_unpublished(html_text):
    """Turn links to posts that aren't published yet into plain text (they'd 404 until their date)."""
    live = {p["slug"] for p in POSTS}
    def repl(m):
        return m.group(0) if m.group(1) in live else m.group(2)
    return re.sub(r'<a href="/blog/([a-z0-9-]+)/">(.*?)</a>', repl, html_text)


def render_blocks(blocks):
    out = []
    for kind, val in blocks:
        if kind == "p":
            out.append(f"<p>{val}</p>")
        elif kind == "h2":
            out.append(f"<h2>{esc(val)}</h2>")
        elif kind in ("ul", "ol"):
            out.append(f"<{kind}>" + "".join(f"<li>{x}</li>" for x in val) + f"</{kind}>")
    return unlink_unpublished("\n          ".join(out))


def post_html(p):
    url = f"{SITE}/blog/{p['slug']}/"
    pub = p["date"] + "T09:00:00+05:30"
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "BlogPosting", "@id": url + "#article", "headline": p["title"][:110], "description": p["description"], "url": url,
             "mainEntityOfPage": url, "image": f"{SITE}/images/og.jpg", "datePublished": pub, "dateModified": pub, "inLanguage": "en",
             "author": {"@type": "Person", "@id": SITE + "/#person", "name": "Gajraj Singh Shekhawat", "alternateName": "Gajraj Shekhawat", "url": SITE + "/about/"},
             "publisher": {"@type": "Person", "@id": SITE + "/#person", "name": "Gajraj Singh Shekhawat"},
             "keywords": ", ".join(p["tags"])},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Gajraj Singh Shekhawat", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog/"},
                {"@type": "ListItem", "position": 3, "name": p["title"], "item": url}]},
        ],
    }
    chips = "".join(f"<li>{esc(x)}</li>" for x in p["tags"])
    more = "".join(f'<li><a href="/blog/{o["slug"]}/">{esc(o["title"])} <span aria-hidden="true">→</span></a></li>' for o in [o for o in POSTS if o is not p][:6])
    body = f"""    <section class="hero hero--page">
      <div class="hero__bg" aria-hidden="true"><span class="blob blob--1"></span><span class="blob blob--2"></span><span class="grid"></span></div>
      <div class="wrap">
        <nav class="crumbs load" aria-label="Breadcrumb"><a href="/">Gajraj Singh Shekhawat</a> <span aria-hidden="true">/</span> <a href="/blog/">Blog</a></nav>
        <p class="post-meta load" style="--d:1"><img src="/images/avatar-96.webp" alt="" width="28" height="28" /><span>By <a href="/about/" rel="author">Gajraj Singh Shekhawat</a></span><span aria-hidden="true">·</span><time datetime="{p["date"]}">{fmt_date(p["date"])}</time></p>
        <h1 class="page-title page-title--post load" style="--d:2">{esc(p["title"])}</h1>
        <p class="lead load" style="--d:3">{esc(p["summary"])}</p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <article class="article reveal">
          {render_blocks(p["body"])}
        </article>
        <ul class="chips page-chips article__tags">{chips}</ul>
        <aside class="article__cta reveal" aria-label="Get help">
          <p class="article__cta-title">Need help building this?</p>
          <p>I'm Gajraj Singh Shekhawat, a full-stack software engineer from Jaipur. With my small team I build websites, apps, e-commerce, EdTech platforms and AI tools for businesses in India and worldwide. Tell me what you need and I'll reply within a day.</p>
          <div class="hero__cta">
            <a href="/#contact" class="btn btn--primary">Send a message <span class="btn__arrow" aria-hidden="true">→</span></a>
            <a href="{WA}" class="btn btn--ghost" target="_blank" rel="noopener">WhatsApp</a>
          </div>
        </aside>
        <div class="article__author reveal">
          <img src="/images/avatar-96.webp" alt="Gajraj Singh Shekhawat" width="56" height="56" loading="lazy" />
          <p><strong>Gajraj Singh Shekhawat</strong> is a full-stack software engineer from Jaipur, India, building backends, apps, e-commerce and AI. <a href="/about/">About Gajraj</a> · <a href="/#contact">Contact</a></p>
        </div>
      </div>
    </section>

    <section class="section section--alt">
      <div class="wrap">
        <nav class="other-services reveal" aria-label="More articles">
          <p class="footer__label">More articles</p>
          <ul>{more}</ul>
        </nav>
      </div>
    </section>"""
    return shell(p["title"] + " · Gajraj Singh Shekhawat" if len(p["title"]) <= 40 else p["title"], p["description"], url, ld, body, "article")


def blog_index_html():
    url = f"{SITE}/blog/"
    title = "Blog · Gajraj Singh Shekhawat, Software Engineer"
    description = "Articles and case studies by Gajraj Singh Shekhawat on backends, AI agents, e-commerce, performance and business websites."
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Blog", "@id": url + "#blog", "name": "Gajraj Singh Shekhawat · Blog", "url": url, "description": description, "inLanguage": "en",
             "author": {"@type": "Person", "@id": SITE + "/#person", "name": "Gajraj Singh Shekhawat"},
             "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}/blog/{p['slug']}/", "datePublished": p["date"]} for p in POSTS]},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Gajraj Singh Shekhawat", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": url}]},
        ],
    }
    cards = "".join(f"""
          <a class="post-card reveal" href="/blog/{p["slug"]}/">
            <p class="post-card__meta"><time datetime="{p["date"]}">{fmt_date(p["date"])}</time> · {esc(", ".join(p["tags"][:3]))}</p>
            <h2>{esc(p["title"])}</h2>
            <p>{esc(p["summary"])}</p>
            <span class="post-card__more">Read article →</span>
          </a>""" for p in POSTS)
    cases = "".join(f'<li><a href="/work/{c["slug"]}/">{esc(c["name"])} case study <span aria-hidden="true">→</span></a></li>' for c in CASES)
    body = f"""    <section class="hero hero--page">
      <div class="hero__bg" aria-hidden="true"><span class="blob blob--1"></span><span class="blob blob--2"></span><span class="grid"></span></div>
      <div class="wrap">
        <nav class="crumbs load" aria-label="Breadcrumb"><a href="/">Gajraj Singh Shekhawat</a> <span aria-hidden="true">/</span> <span>Blog</span></nav>
        <p class="eyebrow load" style="--d:1">Blog</p>
        <h1 class="page-title load" style="--d:2">Notes from <em>building real software</em></h1>
        <p class="lead load" style="--d:3">Articles by Gajraj Singh Shekhawat on backends, AI agents, e-commerce, performance and websites for small businesses, drawn from projects in production.</p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="post-list">{cards}
        </div>
        <nav class="other-services reveal" aria-label="Case studies">
          <p class="footer__label">Case studies</p>
          <ul>{cases}</ul>
        </nav>
      </div>
    </section>"""
    return shell(title, description, url, ld, body)


def rss_feed():
    import email.utils
    items = "".join(f"""
    <item>
      <title>{esc(p["title"])}</title>
      <link>{SITE}/blog/{p["slug"]}/</link>
      <guid isPermaLink="true">{SITE}/blog/{p["slug"]}/</guid>
      <pubDate>{email.utils.format_datetime(datetime.datetime.fromisoformat(p["date"] + "T09:00:00+05:30"))}</pubDate>
      <dc:creator>Gajraj Singh Shekhawat</dc:creator>
      <description>{esc(p["description"])}</description>
      {"".join(f"<category>{esc(t)}</category>" for t in p["tags"])}
    </item>""" for p in sorted(POSTS, key=lambda x: x["date"], reverse=True))
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>Gajraj Singh Shekhawat · Blog</title>
    <link>{SITE}/blog/</link>
    <atom:link href="{SITE}/blog/feed.xml" rel="self" type="application/rss+xml" />
    <description>Articles by Gajraj Singh Shekhawat, full-stack software engineer from Jaipur, on backends, AI, e-commerce and websites.</description>
    <language>en</language>{items}
  </channel>
</rss>
"""


def refresh_llms_blog():
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8")
    text = re.split(r"\n## Blog\n", text)[0].rstrip("\n")
    lines = "".join(f"- [{p['title']}]({SITE}/blog/{p['slug']}/): {p['summary']}\n" for p in POSTS)
    path.write_text(text + "\n\n## Blog\n\n" + lines, encoding="utf-8")


def shell(title, description, url, ld, body, og_type="website"):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />
  <meta name="author" content="Gajraj Singh Shekhawat" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1" />
  <link rel="canonical" href="{url}" />
  <meta name="theme-color" content="#09090b" />
  <meta property="og:type" content="{og_type}" />
  <meta property="og:site_name" content="Gajraj Singh Shekhawat" />
  <meta property="og:url" content="{url}" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description)}" />
  <meta property="og:image" content="{SITE}/images/og.jpg" />
  <link rel="alternate" type="application/rss+xml" title="Gajraj Singh Shekhawat · Blog" href="{SITE}/blog/feed.xml" />
  <link rel="author" href="{SITE}/about/" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="{SITE}/images/og.jpg" />
  <link rel="icon" href="/images/favicon-32.png" sizes="32x32" type="image/png" />
  <link rel="apple-touch-icon" href="/images/apple-touch-icon.png" />
  <link rel="preload" href="/fonts/geist.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/fonts/instrument-serif-italic.woff2" as="font" type="font/woff2" crossorigin />
  {GH_REDIRECT}
  <link rel="stylesheet" href="/styles.min.css" />
  <script>
    document.documentElement.classList.add('js');
    try {{ var t = localStorage.getItem('theme'); if (t) document.documentElement.dataset.theme = t; }} catch (e) {{}}
  </script>
  <script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
  </script>
</head>
<body class="subpage">
  <a class="skip" href="#main">Skip to content</a>
  <div class="progress" aria-hidden="true"><span id="progressBar"></span></div>
{nav_html()}

  <main id="main">
{body}
  </main>

{footer_html()}

  <a href="#top" class="totop" id="toTop" aria-label="Back to top">
    <svg viewBox="0 0 48 48" aria-hidden="true"><circle class="totop__track" cx="24" cy="24" r="21" /><circle class="totop__bar" cx="24" cy="24" r="21" /></svg>
    <span aria-hidden="true">↑</span>
  </a>
  <div class="cursor" aria-hidden="true"><span class="cursor__dot"></span><span class="cursor__ring"></span></div>
  <script src="/script.js" defer></script>
</body>
</html>
'''


def _normalise(text):
    text = re.sub(r"\?v=[0-9a-f]+", "", text)
    text = re.sub(r'"date(?:Published|Modified)": "[^"]*"', '"date": ""', text)
    return text


def track_lastmod():
    """Record the date each page's content last really changed; stamp that into dateModified."""
    lm = json.loads(LASTMOD_FILE.read_text()) if LASTMOD_FILE.exists() else {}
    targets = {f"{SITE}/": ROOT / "index.html", f"{SITE}/blog/": ROOT / "blog" / "index.html"}
    targets.update({f"{SITE}/{p['slug']}/": ROOT / p["slug"] / "index.html" for p in PAGES})
    targets.update({f"{SITE}/work/{c['slug']}/": ROOT / "work" / c["slug"] / "index.html" for c in CASES})
    for url, path in targets.items():
        text = path.read_text(encoding="utf-8")
        h = hashlib.sha1(_normalise(text).encode()).hexdigest()
        if lm.get(url, {}).get("hash") != h:
            lm[url] = {"hash": h, "date": TODAY}
        stamped = re.sub(r'"dateModified": "[^"]*"', f'"dateModified": "{lm[url]["date"]}"', text)
        if stamped != text:
            path.write_text(stamped, encoding="utf-8")
    pdf = ROOT / "assets" / "Gajraj-Shekhawat-Resume.pdf"
    url = f"{SITE}/assets/Gajraj-Shekhawat-Resume.pdf"
    h = hashlib.sha1(pdf.read_bytes()).hexdigest()
    if lm.get(url, {}).get("hash") != h:
        lm[url] = {"hash": h, "date": TODAY}
    LASTMOD_FILE.write_text(json.dumps(lm, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return lm


def sitemap(lm):
    def d(u):
        return lm[u]["date"]
    urls = [(f"{SITE}/", d(f"{SITE}/"), "1.0", f"\n    <image:image><image:loc>{SITE}/images/gajraj.jpg</image:loc></image:image>")]
    urls += [(f"{SITE}/{p['slug']}/", d(f"{SITE}/{p['slug']}/"), "0.8", "") for p in PAGES]
    urls += [(f"{SITE}/work/{c['slug']}/", d(f"{SITE}/work/{c['slug']}/"), "0.7", "") for c in CASES]
    urls += [(f"{SITE}/blog/", max([d(f"{SITE}/blog/")] + [p["date"] for p in POSTS]), "0.7", "")]
    urls += [(f"{SITE}/blog/{p['slug']}/", p["date"], "0.6", "") for p in POSTS]
    pdf = f"{SITE}/assets/Gajraj-Shekhawat-Resume.pdf"
    urls += [(pdf, d(pdf), "0.5", "")]
    body = "".join(f"""  <url>
    <loc>{u}</loc>
    <lastmod>{lmd}</lastmod>
    <priority>{pr}</priority>{img}
  </url>
""" for u, lmd, pr, img in urls)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
{body}</urlset>
'''


ASSET_RE = re.compile(
    r'((?:href|src|srcset|content)=")((?:https://gajrajshekhawat\.com)?/?(?:styles\.min\.css|styles\.css|script\.js|images/[^"?\s]+))(?:\?v=[0-9a-f]+)?"')


def asset_version(path):
    return hashlib.md5((ROOT / path).read_bytes()).hexdigest()[:8]


def bust_assets(html_text):
    """Append ?v=<content hash> to CSS, JS and image URLs so every deploy is picked up
    immediately while files can still be cached for a long time."""
    def repl(m):
        url = m.group(2)
        local = re.sub(r"^(https://gajrajshekhawat\.com)?/?", "", url)
        if not (ROOT / local).exists():
            return m.group(0)
        return f'{m.group(1)}{url}?v={asset_version(local)}"'
    return ASSET_RE.sub(repl, html_text)


def minify_css():
    """Write styles.min.css from styles.css (comments + whitespace only; safe for calc())."""
    src = (ROOT / "styles.css").read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,])\s*", r"\1", css)
    css = re.sub(r":\s+", ":", css).replace(";}", "}")
    (ROOT / "styles.min.css").write_text(css.strip() + "\n", encoding="utf-8")
    return len(src), len(css)


if __name__ == "__main__":
    print("css minified %d -> %d bytes" % minify_css())
    for p in PAGES:
        out = ROOT / p["slug"] / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(page_html(p), encoding="utf-8")
        print("built", out.relative_to(ROOT))
    for c in CASES:
        out = ROOT / "work" / c["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(case_html(c), encoding="utf-8")
        print("built", out.relative_to(ROOT))
    (ROOT / "blog").mkdir(exist_ok=True)
    (ROOT / "blog" / "index.html").write_text(blog_index_html(), encoding="utf-8")
    print("built blog/index.html")
    (ROOT / "blog" / "feed.xml").write_text(rss_feed(), encoding="utf-8")
    print("built blog/feed.xml")
    refresh_llms_blog()
    for p in POSTS:
        out = ROOT / "blog" / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(post_html(p), encoding="utf-8")
        print("built", out.relative_to(ROOT))
    for page in [ROOT / "404.html", *ROOT.rglob("index.html")]:
        if "node_modules" in page.parts:
            continue
        text = page.read_text(encoding="utf-8")
        text = re.sub(r'href="(/?)styles\.css(\?v=[0-9a-f]+)?"', r'href="\1styles.min.css"', text)
        busted = bust_assets(text)
        if busted != text:
            page.write_text(busted, encoding="utf-8")
    print("asset versions refreshed")
    lm = track_lastmod()
    (ROOT / "sitemap.xml").write_text(sitemap(lm), encoding="utf-8")
    print("sitemap.xml updated with", len(PAGES) + len(CASES) + len(POSTS) + 3, "URLs")
