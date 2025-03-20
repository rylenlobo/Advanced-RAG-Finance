"use client";
import { motion } from "framer-motion";
import { ArrowRight, Loader } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { memo, useState } from "react";
import { useQueryClient, useMutation } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { v4 as uuidv4 } from "uuid";
import useDocumentStore from "@/store/currentDocStore";
import { query } from "@/network/query";
import { supabase } from "@/utils/supabase/client/supabase-client";
import { toast } from "sonner";

function InputAI() {
  const [inputValue, setInputValue] = useState("");
  const router = useRouter();
  const queryClient = useQueryClient();
  const { id: conversationId } = useParams<{ id: string }>();
  const { selectedDocumentDetails } = useDocumentStore();
  const isNewChat = conversationId === undefined ? true : false;

  const sendMessageMutation = useMutation({
    mutationFn: async (params: {
      message: string;
      tempIds: { conversationId: string; messageId: string };
    }) => {
      const { message, tempIds } = params;
      const {
        data: { user }
      } = await supabase.auth.getUser();

      if (
        !selectedDocumentDetails?.id ||
        !selectedDocumentDetails?.file_name ||
        !user?.id
      ) {
        throw new Error("Missing required document or user information");
      }

      return query({
        query_id: tempIds.messageId,
        query: message,
        conversation_id: tempIds.conversationId,
        document_id: selectedDocumentDetails.id,
        file_name: selectedDocumentDetails.file_name,
        user_id: user.id
      });
    },

    onMutate: async (params) => {
      const { message, tempIds } = params;
      // Use the IDs passed from handleSend
      const { conversationId: tempConversationId, messageId } = tempIds;

      await queryClient.cancelQueries({
        queryKey: ["conversations", selectedDocumentDetails?.id]
      });

      // Create message object using passed IDs
      const messageObj = {
        id: messageId,
        content: message,
        role: "user",
        conversation_id: tempConversationId
      };

      // Create a loading message
      const loadingMessageId = uuidv4();
      const loadingMessage = {
        id: loadingMessageId,
        content: "...",
        role: "assistant",
        conversation_id: tempConversationId,
        isLoading: true // Custom property to identify loading message
      };

      // Store previous data
      const previousConversations = queryClient.getQueryData([
        "conversations",
        selectedDocumentDetails?.id
      ]);

      if (isNewChat) {
        // Create optimistic chat entry for sidebar
        const newChat = {
          id: tempConversationId,
          name: "New Chat",
          document_id: selectedDocumentDetails?.id
        };

        // Update conversations list
        queryClient.setQueryData(
          ["conversations", selectedDocumentDetails?.id],
          (old: any) => {
            return {
              pages: [
                {
                  data: [newChat, ...(old?.pages[0]?.data || [])],
                  nextId: old?.pages[0]?.nextId
                },
                ...(old?.pages.slice(1) || [])
              ],
              pageParams: old?.pageParams || [0]
            };
          }
        );
        router.push(`/chat/${tempConversationId}`);

        // Initialize the messages for this conversation - include loading message
        queryClient.setQueryData(["messages", tempConversationId], {
          pages: [
            {
              data: [loadingMessage, messageObj],
              nextId: null
            }
          ],
          pageParams: [0]
        });
      } else {
        queryClient.setQueryData(["messages", conversationId], (old: any) => ({
          pages: [
            {
              data: [
                loadingMessage, // Add loading message first
                messageObj,
                ...(old?.pages[0]?.data || [])
              ],
              nextId: old?.pages[0]?.nextId
            },
            ...(old?.pages.slice(1) || [])
          ],
          pageParams: old?.pageParams || [0]
        }));
      }

      return {
        previousConversations,
        tempConversationId,
        messageId,
        loadingMessageId
      };
    },

    onSuccess: (response, _, context) => {
      const conversationToUpdate = isNewChat
        ? context?.tempConversationId
        : conversationId;

      // Add assistant's response to the messages - replacing loading message
      queryClient.setQueryData(
        ["messages", conversationToUpdate],
        (old: any) => {
          // Filter out the loading message
          const filteredMessages = old.pages[0].data.filter(
            (msg: any) => !msg.isLoading
          );

          return {
            pages: [
              {
                data: [
                  response, // Real response from server
                  ...filteredMessages
                ],
                nextId: old.pages[0].nextId
              },
              ...old.pages.slice(1)
            ],
            pageParams: old.pageParams
          };
        }
      );

      // // If server returned a different ID than our temp one, we need to redirect
      // if (
      //   isNewChat &&
      //   response.conversation_id !== context?.tempConversationId
      // ) {
      //   router.replace(`/chat/${response.conversation_id}`);

      //   // Invalidate the conversations to get the server's version
      //   queryClient.invalidateQueries({
      //     queryKey: ["conversations", selectedDocumentDetails?.id]
      //   });
      // }
    },

    onError: (_, __, context) => {
      // Roll back to previous state on error
      queryClient.setQueryData(
        ["conversations", selectedDocumentDetails?.id],
        context?.previousConversations
      );

      // Navigate to the new conversation
      router.push(`/`);
      toast.error("An unexpected error occured", {
        position: "top-center"
      });

      // Show error message to user
      // You could add a toast notification here
    }
  });

  const handleSend = () => {
    if (!inputValue.trim()) return;

    // Generate IDs once here
    const tempIds = {
      messageId: uuidv4(),
      conversationId: isNewChat ? uuidv4() : conversationId
    };

    // Pass both message and IDs
    sendMessageMutation.mutate({
      message: inputValue,
      tempIds
    });

    // Clear input after sending
    setInputValue("");
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  return (
    <motion.div
      viewport={{ once: true }}
      layoutId="search-input"
      className="relative"
    >
      <Input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyPress}
        placeholder="Ask whatever you want..."
        className="h-14 w-full rounded-full bg-secondary px-4 py-4"
      />
      <Button
        size="icon"
        onClick={handleSend}
        disabled={sendMessageMutation.isPending}
        className="absolute bottom-0 right-3 top-1/2 -translate-y-1/2 rounded-full"
      >
        <ArrowRight className="h-4 w-4 md:h-5 md:w-5" />
      </Button>
    </motion.div>
  );
}

export default InputAI;
