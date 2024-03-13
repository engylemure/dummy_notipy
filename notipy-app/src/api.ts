export interface Notification {
  id: number;
  content: string;
  viewed: boolean;
  user_id: number;
  deleted: boolean;
}

const host = "http://localhost:8081";

export function notificationsPath(userId: number) {
  return `users/${userId}/notifications`;
}

export async function getNotifications(userId: number): Promise<Notification[]> {
  const response = await fetch(`${host}/${notificationsPath(userId)}`);
  if (response.ok) {
    return response.json();
  } else {
    throw response;
  }
}

export async function updateNotification({
  id,
  user_id,
  viewed,
  deleted,
}: Notification): Promise<Notification> {
  const response = await fetch(`${host}/${notificationsPath(user_id)}/${id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ viewed, deleted }),
  });
  if (response.ok) {
    return response.json();
  } else {
    throw response;
  }
}

export  async function createNotification(
  user_id: number,
  content: string
): Promise<Notification> {
  const response = await fetch(`${host}/${notificationsPath(user_id)}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ content }),
  });
  if (response.ok) {
    return response.json();
  } else {
    throw response;
  }
}
