import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { getDocuments, uploadDocument } from "../services/api";

export function useDocuments() {
  return useQuery({
    queryKey: ["documents"],
    queryFn: getDocuments,
  });
}

export function useUploadDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => uploadDocument(file),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["documents"] }),
  });
}
