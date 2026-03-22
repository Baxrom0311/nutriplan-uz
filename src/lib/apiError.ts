import axios from "axios";

const flattenMessages = (value: unknown): string[] => {
  if (typeof value === "string") {
    return [value];
  }

  if (Array.isArray(value)) {
    return value.flatMap(flattenMessages);
  }

  if (value && typeof value === "object") {
    return Object.values(value).flatMap(flattenMessages);
  }

  return [];
};

export const getApiErrorMessage = (error: unknown, fallback: string): string => {
  if (!axios.isAxiosError(error)) {
    return fallback;
  }

  const data = error.response?.data;

  if (data && typeof data === "object") {
    const response = data as {
      detail?: string;
      message?: string;
      errors?: unknown;
    };

    if (typeof response.detail === "string") {
      return response.detail;
    }

    if (response.errors) {
      const errorMessages = flattenMessages(response.errors);
      if (errorMessages.length > 0) {
        return errorMessages.join(" ");
      }
    }

    if (typeof response.message === "string") {
      return response.message;
    }

    const messages = flattenMessages(response);
    if (messages.length > 0) {
      return messages.join(" ");
    }
  }

  return error.message || fallback;
};
