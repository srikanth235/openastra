"use client";

import { MoreHorizontal, PenLine, Plus, Timer, Upload, Bot, Sparkles, Trash2 } from "lucide-react";
import * as React from "react";
import { useState, useEffect, useRef, useCallback } from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import type { Project } from "@/lib/types";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

import { useProject } from "./project-provider";
import { toast } from "sonner";
import { useSession } from "next-auth/react";
import { getToken } from "@/lib/utils";

interface ProjectProps {
  data?: Project;
  isLoading?: boolean;
}

export function Project({ isLoading, data }: ProjectProps) {
  const { updateProject, deleteProject } = useProject();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadQueue, setUploadQueue] = useState<Array<string>>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [editingField, setEditingField] = useState<string | null>(null);
  const [editedValues, setEditedValues] = useState({
    title: data?.title || "",
    description: data?.description || "",
    instructions: data?.instructions || "",
  });
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isDeletingFile, setIsDeletingFile] = useState<string | null>(null);
  const { data: session } = useSession();
  const token = getToken(session);
  const [fileToDelete, setFileToDelete] = useState<string | null>(null);

  const handleSave = async (field: string) => {
    if (!data?.id) return;

    try {
      await updateProject(data.id, {
        [field]: editedValues[field as keyof typeof editedValues],
      });
      setEditingField(null);
    } catch (error) {
      console.error(`Error saving ${field}:`, error);
      toast.error(`Failed to update ${field}`);
    }
  };

  const handleDelete = async () => {
    if (!data?.id) return;

    try {
      await deleteProject(data.id);
      setIsDeleteDialogOpen(false);
      // The ProjectProvider will handle updating the UI after deletion
    } catch (error) {
      console.error("Error deleting project:", error);
      toast.error("Failed to delete project");
    }
  };

  // Update the editingField state handler to also update editedValues
  const handleEditClick = (field: string) => {
    if (editingField === field) {
      setEditingField(null);
    } else {
      setEditingField(field);
      setEditedValues({
        ...editedValues,
        [field]: data?.[field as keyof Project] || "",
      });
    }
  };

  const handleFileUpload = async (files: File[]) => {
    if (!data?.id) return;

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      console.log("Here..");
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_HOST}/api/v1/files/?project_id=${data.id}`, {
        method: "POST",
        body: formData,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const result = await response.json();
      console.log(result);

      // Update the project with the new file paths
      const updatedFiles = [...(data.files || []), ...result.files];
      await updateProject(data.id, {
        files: updatedFiles,
      });

      toast.success("Files uploaded successfully");
    } catch (error) {
      console.error("Upload error:", error);
      toast.error("Failed to upload files");
    }
  };

  const handleFileDelete = async (filename: string) => {
    if (!data?.id) return;

    try {
      setIsDeletingFile(filename);
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_HOST}/api/v1/files/?file=${filename}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Delete failed");
      }

      // Update the project's files list
      const updatedFiles = data.files?.filter((f) => f !== filename) || [];
      await updateProject(data.id, {
        files: updatedFiles,
      });

      toast.success("File deleted successfully");
    } catch (error) {
      console.error("Delete error:", error);
      toast.error("Failed to delete file");
    } finally {
      setIsDeletingFile(null);
    }
  };

  const handleFileChange = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(event.target.files || []);
      const currentFileCount = data?.files?.length || 0;

      if (currentFileCount + files.length > 5) {
        toast.error("You can only upload a maximum of 5 files");
        return;
      }

      setUploadQueue(files.map((file) => file.name));
      setIsUploading(true);

      try {
        await handleFileUpload(files);
      } finally {
        setUploadQueue([]);
        setIsUploading(false);
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
      }
    },
    [data?.files?.length, data?.id]
  );

  // ... (keeping the loading skeleton JSX as is)

  return (
    <div className="flex  flex-col lg:flex-row p-2 pt-0">
      {/* Right Sidebar */}
      <div className="w-full p-6 bg-secondary  overflow-y-auto">
        <div className="space-y-6">
          {/* Title Section */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold">Title</h2>
              <Button variant="ghost" size="sm" onClick={() => handleEditClick("title")}>
                {editingField === "title" ? "Cancel" : "Edit"}
              </Button>
            </div>
            {editingField === "title" ? (
              <div className="flex gap-2">
                <Input
                  value={editedValues.title}
                  onChange={(e) => setEditedValues({ ...editedValues, title: e.target.value })}
                  className="text-sm"
                />
                <Button size="sm" onClick={() => handleSave("title")}>
                  Save
                </Button>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">{data?.title}</p>
            )}
          </div>
          <Separator className="bg-primary/20" />
          {/* Description Section */}
          {(data?.description || editingField === "description") && (
            <>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h2 className="font-semibold">Description</h2>
                  <Button variant="ghost" size="sm" onClick={() => handleEditClick("description")}>
                    {editingField === "description" ? "Cancel" : "Edit"}
                  </Button>
                </div>
                {editingField === "description" ? (
                  <div className="flex flex-col gap-2">
                    <Textarea
                      value={editedValues.description}
                      onChange={(e) => setEditedValues({ ...editedValues, description: e.target.value })}
                      className="text-sm"
                    />
                    <Button size="sm" onClick={() => handleSave("description")}>
                      Save
                    </Button>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">{data?.description}</p>
                )}
              </div>
              <Separator className="bg-primary/20" />
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

          <Separator className="bg-primary/20" />

          {/* Instructions Section */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <PenLine className="size-4" />
                <h2 className="font-semibold">Instructions</h2>
              </div>
              <Button variant="ghost" size="sm" onClick={() => handleEditClick("instructions")}>
                {editingField === "instructions" ? "Cancel" : "Edit"}
              </Button>
            </div>
            {editingField === "instructions" ? (
              <div className="flex flex-col gap-2">
                <Textarea
                  value={editedValues.instructions}
                  onChange={(e) => setEditedValues({ ...editedValues, instructions: e.target.value })}
                  className="text-sm"
                />
                <Button size="sm" onClick={() => handleSave("instructions")}>
                  Save
                </Button>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">{data?.instructions || "No custom instructions added."}</p>
            )}
          </div>

          <Separator className="bg-primary/20" />

          {/* Updated Files Section */}
          <div className="space-y-4">
            <input
              type="file"
              className="hidden"
              ref={fileInputRef}
              multiple
              onChange={handleFileChange}
              accept="application/pdf,text/*,image/*"
            />
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Upload className="size-4" />
                <h2 className="font-semibold">Files</h2>
                <span className="text-xs text-muted-foreground">({data?.files?.length || 0}/5)</span>
              </div>
              <Button
                size="icon"
                variant="ghost"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading || (data?.files?.length || 0) >= 5}
              >
                <Plus className="size-4" />
              </Button>
            </div>

            {uploadQueue.length > 0 && (
              <div className="space-y-2">
                {uploadQueue.map((filename) => (
                  <div key={filename} className="text-sm text-muted-foreground flex items-center gap-2">
                    <Timer className="size-4 animate-spin" />
                    <span>Uploading {filename}...</span>
                  </div>
                ))}
              </div>
            )}

            {data?.files && data.files.length > 0 && (
              <ul className="space-y-2">
                {data.files.map((file, index) => (
                  <li key={index} className="text-sm flex items-center justify-between">
                    <span className="truncate flex-1 mr-2">{file.split("/").pop()?.slice(16)}</span>
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setFileToDelete(file)}
                          disabled={isDeletingFile === file}
                        >
                          {isDeletingFile === file ? (
                            <Timer className="size-4 animate-spin" />
                          ) : (
                            <Trash2 className="size-4" />
                          )}
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                          <AlertDialogDescription>
                            This action cannot be undone. This will permanently delete the file.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction onClick={() => fileToDelete && handleFileDelete(fileToDelete)}>
                            Delete
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
