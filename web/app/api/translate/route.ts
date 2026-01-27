import { NextResponse } from 'next/server'

type Body = {
  text: string
  direction: 'forward' | 'reverse'
}

const dict: Record<string, string> = {
  'no cap': 'that is the truth',
  'fr fr': 'i am being serious',
  'fit is fire': 'the outfit looks amazing',
  'bro’s cooked': 'he messed up badly',
  'mood off': 'i am not in a good mood',
}

async function callHF(model: string, token: string, input: string): Promise<string | null> {
  try {
    const res = await fetch(`https://api-inference.huggingface.co/models/${model}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ inputs: input }),
    })
    if (!res.ok) return null
    const data = await res.json()
    const item = Array.isArray(data) ? data[0] : data
    const out = item?.generated_text ?? item?.output ?? null
    if (typeof out === 'string' && out.trim().length > 0) return out
    return null
  } catch {
    return null
  }
}

export async function POST(request: Request) {
  const { text, direction } = (await request.json()) as Body
  const token = process.env.HF_TOKEN
  const forwardModel = process.env.FORWARD_MODEL_ID || process.env.HINGLISH_FORWARD_MODEL_ID
  const reverseModel = process.env.REVERSE_MODEL_ID || process.env.HINGLISH_REVERSE_MODEL_ID

  let output: string | null = null

  if (token) {
    const model = direction === 'forward' ? forwardModel : reverseModel
    if (model) {
      output = await callHF(model, token, text)
    }
  }

  if (!output) {
    const t = text.toLowerCase()
    const found = Object.keys(dict).find((k) => t.includes(k))
    output = found ? dict[found] : 'interpreted meaning not found'
  }

  return NextResponse.json({ output })
}
