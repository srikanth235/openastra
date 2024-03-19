import type { NextApiRequest, NextApiResponse } from "next"
import * as cheerio from "cheerio"

interface Source {
  title: string
  url: string
  description: string
}
export const runtime = "edge"

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)

  const searchQuery = searchParams.get("q") || ""

  try {
    const searchUrl = `https://www.bing.com/search?q=${encodeURIComponent(
      searchQuery
    )}`
    const response = await fetch(searchUrl)
    const html = await response.text()

    const $ = cheerio.load(html)
    const searchResults = $(".b_algo")
    const sources: Source[] = []

    searchResults.each((index, element) => {
      const $result = $(element)
      const title = $result.find("h2 a").text()
      const url = $result.find("h2 a").attr("href") || ""
      const description = $result.find(".b_caption p").text()

      sources.push({ title, url, description })
    })

    return Response.json({ sources })
  } catch (err) {}
}
