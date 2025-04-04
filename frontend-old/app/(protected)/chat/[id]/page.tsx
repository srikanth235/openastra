import { CoreMessage, Message } from "ai";
import { notFound, redirect } from "next/navigation";
import { signOut } from "next-auth/react";

import { auth } from "@/app/(auth)/auth";
import { Chat as PreviewChat } from "@/components/custom/chat";
import { Chat, PageProps } from "@/lib/types";
import { convertToUIMessages, getToken } from "@/lib/utils";

export default async function Page({ params }: PageProps) {
  const resolvedParams = await params; // Await params
  const { id } = resolvedParams;
  const session = await auth();

  if (!session || !session.user) {
    return notFound();
  }

  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/chats/${id}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getToken(session)}`,
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        return notFound();
      } else if (response.status === 401) {
        // Sign out and redirect to sign-in page
        await signOut({ redirect: false });
        redirect("/sign-in");
      }
      throw new Error("Failed to fetch chat");
    }

    const chatFromApi = await response.json();

    // type casting
    const chat: Chat = {
      ...chatFromApi,
      messages: convertToUIMessages(chatFromApi.messages as Array<CoreMessage>),
    };

    if (session.user.id !== chat.userId) {
      return notFound();
    }

    return (
      <div className="flex flex-col h-[calc(100vh-4rem)]">
        <PreviewChat id={chat.id} project={chat.project} initialMessages={(chat!.messages as Array<Message>) || []} />
      </div>
    );
  } catch (error) {
    console.error("Error fetching chat:", error);
    return notFound();
  }
}
