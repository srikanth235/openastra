import { useSession } from "next-auth/react";
import { useState, useEffect } from "react";
import { toast } from "sonner";
import useSWRMutation from "swr/mutation";

import { InviteMemberDialog } from "@/components/custom/invite-member";
import { TeamHeader } from "@/components/custom/team-header";
import { MembersList } from "@/components/custom/team-members";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { getToken } from "@/lib/utils";

interface TeamProps {
  team: any;
  members: any[];
  isLoading: boolean;
  mutateTeam: (data: any) => void;
  mutateMembers: () => void;
  teamId: string;
}

function useUpdateTeam(teamId: string, token: string | undefined) {
  return useSWRMutation(
    token ? [`${process.env.NEXT_PUBLIC_API_URL}/api/v1/teams/${teamId}`, token] : null,
    async ([url, token], { arg }: { arg: { name?: string; description?: string } }) => {
      const response = await fetch(url, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(arg),
      });
      if (!response.ok) throw new Error("Failed to update team");
      return response.json();
    }
  );
}

function useInviteMembers(teamId: string, token: string | undefined) {
  return useSWRMutation(
    token ? [`${process.env.NEXT_PUBLIC_API_URL}/api/v1/teams/${teamId}/members`, token] : null,
    async ([url, token], { arg }: { arg: { email: string }[] }) => {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(arg),
      });
      if (!response.ok) throw new Error("Failed to send invitations");
      return response.json();
    }
  );
}

function useUpdateMemberRole(teamId: string, token: string | undefined) {
  return useSWRMutation(
    token ? [`${process.env.NEXT_PUBLIC_API_URL}/api/v1/teams/${teamId}/members`, token] : null,
    async ([url, token], { arg }: { arg: { userId: string; role: string } }) => {
      const response = await fetch(`${url}/${arg.userId}`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ role: arg.role }),
      });
      if (!response.ok) throw new Error("Failed to update role");
      return response.json();
    }
  );
}

export function Team({ team, members, isLoading, mutateTeam, mutateMembers, teamId }: TeamProps) {
  // State
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [isEditingDescription, setIsEditingDescription] = useState(false);
  const [tempTitle, setTempTitle] = useState("");
  const [tempDescription, setTempDescription] = useState("");
  const [emailList, setEmailList] = useState<string[]>([]);
  const [currentEmail, setCurrentEmail] = useState("");
  const [isInviteDialogOpen, setIsInviteDialogOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentTab, setCurrentTab] = useState("members");
  const { data: session } = useSession();

  const roles = ["owner", "admin", "member"];

  useEffect(() => {
    if (team) {
      setTempTitle(team.name);
      setTempDescription(team.description);
    }
  }, [team]);

  // Mutation hooks
  const { trigger: updateTeam } = useUpdateTeam(teamId, getToken(session));
  const { trigger: inviteMembers } = useInviteMembers(teamId, getToken(session));
  const { trigger: updateRole } = useUpdateMemberRole(teamId, getToken(session));

  // Handlers
  const handleTitleSubmit = async () => {
    if (tempTitle === team.name) {
      setIsEditingTitle(false);
      return;
    }

    try {
      await updateTeam({ name: tempTitle });
      mutateTeam({ ...team, name: tempTitle });
      setIsEditingTitle(false);
      toast.success("Team name updated successfully");
    } catch (error) {
      console.error("Error updating team name:", error);
      toast.error("Failed to update team name");
    }
  };

  const handleDescriptionSubmit = async () => {
    if (tempDescription === team.description) {
      setIsEditingDescription(false);
      return;
    }

    try {
      await updateTeam({ description: tempDescription });
      mutateTeam({ ...team, description: tempDescription });
      setIsEditingDescription(false);
      toast.success("Team description updated successfully");
    } catch (error) {
      console.error("Error updating team description:", error);
      toast.error("Failed to update team description");
    }
  };

  const handleAddEmail = (e: React.FormEvent) => {
    e.preventDefault();
    if (currentEmail && !emailList.includes(currentEmail)) {
      setEmailList([...emailList, currentEmail]);
      setCurrentEmail("");
    }
  };

  const removeEmail = (emailToRemove: string) => {
    setEmailList(emailList.filter((email) => email !== emailToRemove));
  };

  const handleInviteMember = async () => {
    setIsSubmitting(true);
    try {
      await inviteMembers(emailList.map((email) => ({ email })));
      mutateMembers();
      setIsInviteDialogOpen(false);
      setEmailList([]);
      setCurrentEmail("");
      toast.success("Invitations sent successfully");
    } catch (error) {
      console.error("Error inviting members:", error);
      toast.error("Failed to send invitations");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      await updateRole({ userId, role: newRole });
      mutateMembers();
      toast.success("Member role updated successfully");
    } catch (error) {
      console.error("Error updating member role:", error);
      toast.error("Failed to update member role");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent, submitFunction: () => void) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submitFunction();
    }
  };
  const acceptedMembers = members?.filter((member: any) => member.invitation_status === "accepted") || [];
  const pendingMembers = members?.filter((member: any) => member.invitation_status === "pending") || [];

  if (!team || !members) {
    return (
      <div className="flex-1 bg-background">
        <div className="max-w-6xl mx-auto p-6 md:px-32">
          <Card className="border-none shadow-none">
            <CardHeader className="px-2 flex flex-col sm:flex-row justify-between items-start">
              <div className="space-y-4 w-full sm:w-auto">
                <Skeleton className="h-8 w-64" />
                <Skeleton className="h-16 w-96" />
              </div>
              <div className="w-full sm:w-auto mt-4 sm:mt-0">
                <Skeleton className="h-10 w-32" />
              </div>
            </CardHeader>

            <CardContent className="px-2">
              <Skeleton className="h-10 w-48 mb-4" />
              <div className="space-y-2">
                {[1, 2, 3].map((index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <Skeleton className="size-8 rounded-full" />
                      <div>
                        <Skeleton className="h-4 w-32 mb-2" />
                        <Skeleton className="h-3 w-48" />
                      </div>
                    </div>
                    <Skeleton className="h-8 w-20" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 bg-background">
      <div className="max-w-6xl mx-auto p-6 md:px-32">
        <Card className="border-none shadow-none">
          <CardHeader className="px-2 flex flex-col sm:flex-row justify-between items-start">
            <TeamHeader
              team={team}
              isEditingTitle={isEditingTitle}
              isEditingDescription={isEditingDescription}
              tempTitle={tempTitle}
              tempDescription={tempDescription}
              setIsEditingTitle={setIsEditingTitle}
              setIsEditingDescription={setIsEditingDescription}
              setTempTitle={setTempTitle}
              setTempDescription={setTempDescription}
              handleTitleSubmit={handleTitleSubmit}
              handleDescriptionSubmit={handleDescriptionSubmit}
              handleKeyPress={handleKeyPress}
            />

            <div className="w-full sm:w-auto mt-4 sm:mt-0">
              <InviteMemberDialog
                isOpen={isInviteDialogOpen}
                setIsOpen={setIsInviteDialogOpen}
                emailList={emailList}
                currentEmail={currentEmail}
                setCurrentEmail={setCurrentEmail}
                handleAddEmail={handleAddEmail}
                removeEmail={removeEmail}
                handleInviteMember={handleInviteMember}
                isSubmitting={isSubmitting}
              />
            </div>
          </CardHeader>

          <CardContent className="px-2">
            <Tabs value={currentTab} onValueChange={setCurrentTab}>
              <TabsList className="mb-4">
                <TabsTrigger value="members">Members</TabsTrigger>
                <TabsTrigger value="pendingInvites">Pending Invites</TabsTrigger>
              </TabsList>

              <TabsContent value="members">
                <MembersList members={acceptedMembers} roles={roles} handleRoleChange={handleRoleChange} />
              </TabsContent>

              <TabsContent value="pendingInvites">
                <MembersList
                  members={pendingMembers}
                  roles={roles}
                  handleRoleChange={handleRoleChange}
                  isPending={true}
                />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
