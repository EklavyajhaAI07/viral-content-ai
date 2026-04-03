import type {
  ContentData,
  StrategyData,
  TrendItem,
  User,
  ViralityData,
} from "@/types";

const pick = <T,>(items: T[], count: number) =>
  items
    .slice()
    .sort(() => 0.5 - Math.random())
    .slice(0, count);

export function createDemoUser(name = "Demo Creator"): User {
  const username = name.toLowerCase().replace(/\s+/g, "-");

  return {
    id: Date.now(),
    email: `${username}@demo.local`,
    username,
    full_name: name,
    plan: "demo",
    is_active: true,
  };
}

export function generateDemoTrends(topic: string, platform = "all"): TrendItem[] {
  const hashtags = [
    `#${topic.replace(/\s+/g, "")}`,
    "#CreatorEconomy",
    "#DigitalMarketing",
    "#GrowthPlaybook",
    "#SocialSignals",
    "#ViralHooks",
    "#AudienceFirst",
    "#TrendWatch",
  ];

  const labels = [
    "Micro-hook explainers",
    "Behind-the-scenes proof",
    "Comparison carousel",
    "Myth-busting short",
    "POV storytelling angle",
    "Tool stack breakdown",
    "Beginner mistakes series",
    "Hot take reaction format",
  ];

  return labels.map((label, index) => ({
    topic: `${topic} - ${label}`,
    hashtags: pick(hashtags, 4),
    platforms:
      platform === "all"
        ? pick(["instagram", "tiktok", "youtube", "twitter", "linkedin"], 3)
        : [platform, ...pick(["instagram", "tiktok", "youtube", "twitter", "linkedin"].filter((item) => item !== platform), 2)],
    velocity_score: Math.max(52, 94 - index * 5),
    niche: ["tech", "business", "education", "lifestyle"][index % 4],
    peak_prediction_hours: 4 + index * 5,
    status: index < 3 ? "peak" : index < 6 ? "emerging" : "declining",
  }));
}

export function generateDemoContent(
  topic: string,
  platform = "instagram",
  tone = "engaging",
  audience = "general",
): ContentData {
  return {
    hook: `Stop scrolling: this ${topic} play could change how ${audience} creators grow this month.`,
    caption: `Most people publish about ${topic} with no clear point of view.\n\nTry this instead:\n1. Lead with a sharp promise\n2. Show one specific insight\n3. End with a save-worthy takeaway\n\nThis version is tuned for ${platform} with a ${tone} tone so it feels native, not robotic.\n\nIf you want, turn this into a series and reuse the best-performing opening line.`,
    hashtags: {
      niche: [`#${topic.replace(/\s+/g, "")}Tips`, "#CreatorStrategy", "#AudienceGrowth", "#ContentHooks", "#RetentionPlay"],
      trending: ["#ContentMarketing", "#SocialMediaGrowth", "#BrandStorytelling", "#MarketingIdeas", "#CreatorTips"],
      broad: ["#Viral", "#TrendingNow", "#DigitalCreator", "#SocialMedia", "#Marketing"],
    },
    cta: "Save this idea, test it this week, and share the result with your audience.",
    alternative_hooks: [
      `The ${topic} pattern high-growth creators use quietly`,
      `3 mistakes people make when posting about ${topic}`,
      `What changed when I simplified my ${topic} content strategy`,
    ],
    best_posting_time: "Tuesday to Thursday, 11 AM to 1 PM",
    content_format: platform === "youtube" ? "Short video with data-backed title" : "Short-form video or swipe carousel",
    platform,
    tone,
  };
}

export function generateDemoVirality(topic: string, platform = "instagram"): ViralityData {
  const breakdown = {
    hook_strength: 84,
    hashtag_relevance: 78,
    trend_alignment: 81,
    emotional_tone: 76,
    posting_time_fit: 73,
  };

  return {
    virality_score: 78.4,
    confidence: 0.86,
    grade: "A",
    breakdown,
    predicted_reach: platform === "youtube" ? 62000 : 28400,
    predicted_engagement_rate: 8.7,
    improvements: [
      `Open with a clearer tension point around ${topic} in the first sentence.`,
      "Add one proof element like a stat, result, or personal lesson.",
      "Use a CTA that asks for saves or shares instead of a generic comment prompt.",
    ],
    rewritten_hook: `I studied high-performing ${topic} posts and found one pattern almost everyone misses.`,
  };
}

export function generateDemoStrategy(topic: string, platform = "instagram"): StrategyData {
  const platforms = [platform, "tiktok", "youtube", "linkedin", "twitter"];

  return {
    topic,
    platform,
    calendar: [
      "Audience pain point",
      "Quick tutorial",
      "Behind the scenes",
      "Contrarian take",
      "Social proof story",
      "Myth busting",
      "Weekly recap",
    ].map((angle, index) => ({
      day: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][index],
      date: new Date(Date.now() + index * 86400000).toISOString().slice(0, 10),
      platform: platforms[index % platforms.length],
      content_type: index % 2 === 0 ? "Reel" : "Carousel",
      topic_angle: `${topic} - ${angle}`,
      post_time: ["9:00 AM", "11:30 AM", "1:00 PM", "3:30 PM", "6:00 PM", "10:00 AM", "7:00 PM"][index],
      priority: index < 3 ? "high" : "medium",
    })),
    repurposing_plan: {
      original: `${platform} core post about ${topic}`,
      tiktok: "Turn the best hook into a faster, spoken version with captions.",
      youtube_short: "Use the same structure but add a stronger promise in the title card.",
      linkedin: "Convert the lesson into a professional insight post with one strong takeaway.",
      twitter: "Split the content into a short thread with one point per post.",
    },
    growth_strategy: {
      day_1: {
        title: "Launch window",
        actions: [
          "Reply to early comments within the first 30 minutes.",
          "Share the post to stories or a secondary channel.",
          "Pin a comment that asks for a save or share.",
        ],
      },
      day_2_3: {
        title: "Amplify",
        actions: [
          "Repurpose the strongest line into a second platform format.",
          "Comment on adjacent creators using the same topic cluster.",
          "Pull one audience reaction into a follow-up post.",
        ],
      },
      day_4_7: {
        title: "Iterate",
        actions: [
          "Review retention, saves, and replies for the first three posts.",
          "Repeat the top-performing hook pattern with a new angle.",
          "Bundle the week into a recap carousel or thread.",
        ],
      },
    },
    content_gaps: [
      { gap: `${topic} for complete beginners`, opportunity: "High save rate and broad appeal", viral_potential: "91%" },
      { gap: `${topic} mistakes nobody admits`, opportunity: "Strong comments and relatability", viral_potential: "87%" },
      { gap: `${topic} with proof-based case studies`, opportunity: "Trust-building and repeat views", viral_potential: "84%" },
    ],
    ab_tests: [
      { element: "Opening hook", variant_a: "Bold claim", variant_b: "Contrarian question", metric: "3-second retention" },
      { element: "CTA position", variant_a: "End of caption", variant_b: "Second line", metric: "Saves and shares" },
    ],
    forecast_30_day: {
      follower_growth: "+1.8K followers",
      total_reach: "210K impressions",
      engagement_rate: "7.9%",
      best_performing_day: "Thursday",
      viral_probability: "62%",
    },
  };
}
