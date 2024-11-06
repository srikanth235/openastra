"use client";

import { MoreHorizontal, PenLine, Plus, Timer, Upload, Bot, Sparkles } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import type { Project } from "@/lib/types";
interface ProjectProps {
  data?: Project;
  isLoading?: boolean;
}

export function Project({ isLoading, data }: ProjectProps) {
  let threads = null;
  console.log(data);
  if (isLoading) {
    return (
      <div className="flex min-h-screen flex-col lg:flex-row p-6">
        {/* Main Content Skeleton */}
        <div className="flex-1 p-6 border-r">
          {/* Title skeleton */}
          <Skeleton className="h-8 w-48 mb-8" />

          {/* New thread input skeleton */}
          <Skeleton className="h-32 mb-8" />

          {/* Threads skeleton */}
          <div className="space-y-6">
            <Skeleton className="h-6 w-24" />
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="p-4 space-y-4 border rounded-lg">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-full" />
                  <div className="flex justify-between">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-4 w-8" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar Skeleton */}
        <div className="w-full lg:w-80 p-6 bg-muted/30">
          <div className="space-y-8">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-full" />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col lg:flex-row p-6">
      {/* Main Content */}
      <div className="flex-1 p-6 border-r overflow-y-auto">
        <h1 className="text-3xl font-semibold mb-8">{data?.title}</h1>

        {/* New Thread Input */}
        <Card className="p-4 mb-8">
          <div className="space-y-4">
            <Input className="text-lg border-0 px-0 focus-visible:ring-0" placeholder="New Thread" />
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button variant="ghost" size="sm">
                  None
                </Button>
                <Button variant="ghost" size="sm">
                  <Upload className="size-4 mr-2" />
                  Attach
                </Button>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 bg-muted p-1 rounded-full">
                  <Bot className="size-5" />
                  <Sparkles className="size-5" />
                </div>
                <div className="flex items-center gap-2">
                  {/* <Switch /> */}
                  <span>Pro</span>
                </div>
                <Button size="sm">
                  <PenLine className="size-4 mr-2" />
                  Start
                </Button>
              </div>
            </div>
          </div>
        </Card>

        {/* Threads Section */}
        <div className="space-y-6">
          <div className="flex items-center gap-2">
            <PenLine className="size-4" />
            <h2 className="text-lg font-semibold">Threads</h2>
          </div>

          {threads?.map((thread) => (
            <Card key={thread.id} className="p-4">
              <div className="space-y-4">
                <div className="font-medium">{thread.content}</div>
                <div className="pl-4 border-l-2">{thread.response}</div>
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                      <Timer className="size-4" />
                      <span>{thread.timestamp}</span>
                    </div>
                    <span>{thread.status}</span>
                  </div>
                  <Button variant="ghost" size="icon">
                    <MoreHorizontal className="size-4" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Right Sidebar */}
      <div className="w-full lg:w-80 p-6 bg-muted/30 border-t lg:border-t-0">
        <div className="space-y-6">
          {/* Title Section */}
          <div className="space-y-2">
            <h2 className="font-semibold">Title</h2>
            <p className="text-sm text-muted-foreground">{JSON.stringify(data)}</p>
          </div>

          <Separator />

          {/* Description Section */}
          {data?.description && (
            <>
              <div className="space-y-2">
                <h2 className="font-semibold">Description</h2>
                <p className="text-sm text-muted-foreground">{data?.description}</p>
              </div>
              <Separator />
            </>
          )}

          {/* Model Section */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bot className="size-4" />
                <h2 className="font-semibold">AI Model</h2>
              </div>
            </div>
            <p className="text-sm text-muted-foreground">{data?.model || "Default"}</p>
          </div>

          <Separator />

          {/* Instructions Section */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <PenLine className="size-4" />
                <h2 className="font-semibold">Instructions</h2>
              </div>
              <Button variant="ghost" size="sm">
                Edit
              </Button>
            </div>
            <p className="text-sm text-muted-foreground">{data?.instructions || "No custom instructions added."}</p>
          </div>

          <Separator />

          {/* Files Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Upload className="size-4" />
                <h2 className="font-semibold">Files</h2>
              </div>
              <Button size="icon" variant="ghost">
                <Plus className="size-4" />
              </Button>
            </div>
            {data?.files && data?.files.length > 0 ? (
              <ul className="space-y-2">
                {data?.files.map((file, index) => (
                  <li key={index} className="text-sm flex items-center justify-between">
                    <span>{file}</span>
                    <Button variant="ghost" size="icon">
                      <MoreHorizontal className="size-4" />
                    </Button>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">0 of 5 free files uploaded</p>
                <Button variant="secondary" className="w-full">
                  Upgrade to Pro
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
