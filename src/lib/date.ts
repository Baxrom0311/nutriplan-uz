const padDatePart = (value: number) => String(value).padStart(2, "0");

export const formatDateInputValue = (date: Date): string => {
  const year = date.getFullYear();
  const month = padDatePart(date.getMonth() + 1);
  const day = padDatePart(date.getDate());

  return `${year}-${month}-${day}`;
};

export const getTodayDateInputValue = (): string => formatDateInputValue(new Date());

export const parseDateInputValue = (value: string): Date => {
  const [year, month, day] = value.split("-").map(Number);

  if (!year || !month || !day) {
    return new Date();
  }

  return new Date(year, month - 1, day);
};

export const shiftDateInputValue = (value: string, days: number): string => {
  const date = parseDateInputValue(value);
  date.setDate(date.getDate() + days);
  return formatDateInputValue(date);
};
