"use client";

import { useParams } from "next/navigation";
import { useSession } from "next-auth/react";
import useSWR from "swr";

import { Chat } from "@/components/custom/chat";
import { fetcher, generateUUID, getToken } from "@/lib/utils";

export default function Page() {
  const { id } = useParams();

  const { data: session } = useSession();

  const { data, error, isLoading } = useSWR(
    session?.user
      ? [`${process.env.NEXT_PUBLIC_API_URL}/api/v1/projects/${id}`, getToken(session)]
      : null,
    ([url, token]) => fetcher(url, token)
  );

  return (
    <div className="flex flex-col gap-4 p-4 h-full">
      <Chat id={generateUUID()} project={data} initialMessages={[]} />
    </div>
  );
}
