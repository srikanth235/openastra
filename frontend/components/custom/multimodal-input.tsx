"use client";

import { Attachment, ChatRequestOptions, CreateMessage, Message } from "ai";
import { Paperclip, ChevronDownIcon } from "lucide-react";
import React, { useRef, useEffect, useState, useCallback, Dispatch, SetStateAction, ChangeEvent } from "react";
import { toast } from "sonner";
import { useLocalStorage } from "usehooks-ts";

import { ArrowUpIcon, StopIcon } from "./icons";
import { PreviewAttachment } from "./preview-attachment";
import { Button } from "../ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "../ui/dropdown-menu";
import { Textarea } from "../ui/textarea";

const suggestedActions = [
  {
    title: "What is the weather",
    label: "in San Francisco?",
    action: "what is the weather in San Francisco?",
  },
  {
    title: "Answer like I'm 5,",
    label: "why is the sky blue?",
    action: "Answer like I'm 5, why is the sky blue?",
  },
];

export function MultimodalInput({
  input,
  setInput,
  isLoading,
  stop,
  attachments,
  setAttachments,
  messages,
  append,
  handleSubmit,
}: {
  input: string;
  setInput: (value: string) => void;
  isLoading: boolean;
  stop: () => void;
  attachments: Array<Attachment>;
  setAttachments: Dispatch<SetStateAction<Array<Attachment>>>;
  messages: Array<Message>;
  append: (
    message: Message | CreateMessage,
    chatRequestOptions?: ChatRequestOptions
  ) => Promise<string | null | undefined>;
  handleSubmit: (
    event?: {
      preventDefault?: () => void;
    },
    chatRequestOptions?: ChatRequestOptions
  ) => void;
}) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      adjustHeight();
    }
  }, []);

  const adjustHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  const [localStorageInput, setLocalStorageInput] = useLocalStorage("input", "");
  useEffect(() => {
    if (textareaRef.current) {
      const domValue = textareaRef.current.value;
      // Prefer DOM value over localStorage to handle hydration
      const finalValue = domValue || localStorageInput || "";
      setInput(finalValue);
      adjustHeight();
    }
    // Only run once after hydration
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  useEffect(() => {
    setLocalStorageInput(input);
  }, [input, setLocalStorageInput]);

  const handleInput = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(event.target.value);
    adjustHeight();
  };

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadQueue, setUploadQueue] = useState<Array<string>>([]);

  const submitForm = useCallback(() => {
    handleSubmit(undefined, {
      experimental_attachments: attachments,
    });

    setAttachments([]);
    setLocalStorageInput("");
  }, [attachments, handleSubmit, setAttachments, setLocalStorageInput]);

  const uploadFile = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`/api/files/upload`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        const { url, pathname, contentType } = data;

        return {
          url,
          name: pathname,
          contentType: contentType,
        };
      } else {
        const { error } = await response.json();
        toast.error(error);
      }
    } catch (error) {
      toast.error("Failed to upload file, please try again!");
    }
  };

  const handleFileChange = useCallback(
    async (event: ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(event.target.files || []);

      setUploadQueue(files.map((file) => file.name));

      try {
        const uploadPromises = files.map((file) => uploadFile(file));
        const uploadedAttachments = await Promise.all(uploadPromises);
        const successfullyUploadedAttachments = uploadedAttachments.filter((attachment) => attachment !== undefined);

        setAttachments((currentAttachments) => [...currentAttachments, ...successfullyUploadedAttachments]);
      } catch (error) {
        console.error("Error uploading files!", error);
      } finally {
        setUploadQueue([]);
      }
    },
    [setAttachments]
  );

  const [selectedProject, setSelectedProject] = useState<string | null>(null);

  const randomProjects = ["Cosmic Voyager", "Emerald Nexus", "Quantum Forge"];

  return (
    <div className="relative w-full flex flex-col gap-2">
      <input
        type="file"
        className="fixed -top-4 -left-4 size-0.5 opacity-0 pointer-events-none"
        ref={fileInputRef}
        multiple
        onChange={handleFileChange}
        tabIndex={-1}
      />

      {(attachments.length > 0 || uploadQueue.length > 0) && (
        <div className="flex flex-row gap-2 overflow-x-scroll">
          {attachments.map((attachment) => (
            <PreviewAttachment key={attachment.url} attachment={attachment} />
          ))}

          {uploadQueue.map((filename) => (
            <PreviewAttachment
              key={filename}
              attachment={{
                url: "",
                name: filename,
                contentType: "",
              }}
              isUploading={true}
            />
          ))}
        </div>
      )}

      {/* Textarea wrapper */}
      <div className="grow relative pb-12">
        {" "}
        {/* Adjust padding-bottom here */}
        <Textarea
          ref={textareaRef}
          placeholder="Send a message..."
          value={input}
          onChange={handleInput}
          className="min-h-[12px] max-h-48 border-none overflow-y-auto resize-none rounded-t-lg rounded-b-none text-base bg-muted focus:outline-none  focus-visible:ring-0 focus-visible:ring-offset-0"
          rows={2}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();

              if (isLoading) {
                toast.error("Please wait for the model to finish its response!");
              } else {
                submitForm();
              }
            }
          }}
        />
      </div>

      {/* Action bar */}
      <div className="absolute bottom-0 inset-x-0 flex justify-between items-center py-2 px-4 bg-muted rounded-b-lg">
        <div className="flex space-x-2">
          <Button
            className="p-1.5 size-8 flex items-center justify-center dark:border-zinc-700"
            onClick={(event) => {
              event.preventDefault();
              fileInputRef.current?.click();
            }}
            variant="outline"
            disabled={isLoading}
          >
            <Paperclip size={14} />
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                className="px-2 h-8 flex items-center space-x-1 dark:border-zinc-700"
                variant="outline"
                disabled={isLoading}
              >
                <span>{selectedProject || "Project"}</span>
                <ChevronDownIcon size={14} />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              {randomProjects.map((project) => (
                <DropdownMenuItem key={project} onSelect={() => setSelectedProject(project)}>
                  {project}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {isLoading ? (
          <Button
            className="rounded-full p-1.5 h-fit m-0.5"
            onClick={(event) => {
              event.preventDefault();
              stop();
            }}
          >
            <StopIcon size={14} />
          </Button>
        ) : (
          <Button
            className="p-1.5 h-fit m-0.5"
            onClick={(event) => {
              event.preventDefault();
              handleSubmit(event);
            }}
            disabled={input.length === 0 || uploadQueue.length > 0}
          >
            <ArrowUpIcon size={14} />
          </Button>
        )}
      </div>
    </div>
  );
}
