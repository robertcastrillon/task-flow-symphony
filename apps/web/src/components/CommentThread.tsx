import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { commentFormSchema, type CommentFormData } from "../types";
import { useComments, useCreateComment } from "../hooks/useComments";

interface CommentThreadProps {
  taskId: string;
}

export default function CommentThread({ taskId }: CommentThreadProps) {
  const { data: comments, isLoading } = useComments(taskId);
  const createComment = useCreateComment();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CommentFormData>({
    resolver: zodResolver(commentFormSchema),
  });

  function onSubmit(data: CommentFormData) {
    createComment.mutate({ ...data, taskId }, { onSuccess: () => reset() });
  }

  if (isLoading) {
    return <span className="loading loading-spinner loading-sm"></span>;
  }

  return (
    <div className="space-y-4">
      <h3 className="font-semibold">Comentarios</h3>

      <div className="space-y-3">
        {comments?.length === 0 && (
          <p className="text-sm text-base-content/60">
            No hay comentarios aún.
          </p>
        )}
        {comments?.map((comment) => (
          <div key={comment.id} className="flex gap-3">
            <div className="avatar placeholder">
              <div className="bg-neutral text-neutral-content w-8 rounded-full">
                <span className="text-xs">
                  {comment.author?.name?.charAt(0).toUpperCase() ?? "?"}
                </span>
              </div>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">
                  {comment.author?.name ?? "Usuario"}
                </span>
                <span className="text-xs text-base-content/50">
                  {new Date(comment.created_at).toLocaleString("es")}
                </span>
              </div>
              <p className="text-sm mt-1">{comment.content}</p>
            </div>
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="flex gap-2">
        <input
          type="text"
          placeholder="Escribe un comentario..."
          className={`input input-bordered input-sm flex-1 ${errors.content ? "input-error" : ""}`}
          {...register("content")}
        />
        <button
          type="submit"
          className="btn btn-primary btn-sm"
          disabled={createComment.isPending}
        >
          Enviar
        </button>
      </form>
    </div>
  );
}
