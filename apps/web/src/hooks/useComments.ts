import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../services/api";
import type { Comment, CommentFormData } from "../types";

const COMMENTS_KEY = "comments";

export function useComments(taskId: string) {
  return useQuery({
    queryKey: [COMMENTS_KEY, taskId],
    queryFn: async () => {
      const { data } = await api.get<Comment[]>(`/tasks/${taskId}/comments`);
      return data;
    },
    enabled: !!taskId,
  });
}

export function useCreateComment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      taskId,
      ...commentData
    }: CommentFormData & { taskId: string }) => {
      const { data } = await api.post<Comment>(
        `/tasks/${taskId}/comments`,
        commentData,
      );
      return data;
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: [COMMENTS_KEY, variables.taskId],
      });
    },
  });
}
