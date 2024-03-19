import { Message } from "ai/react"

export function Question({ message }: { message: Message }) {
  return (
    <>
      <div className="col-span-1 p-4 lg:col-span-2">
        <div className="rounded-md ">
          <h2 className="mb-2 text-xl font-bold">{message.content}</h2>
        </div>
      </div>
      <div className="col-span-1">
        <div className="rounded-md "></div>
      </div>
    </>
  )
}
