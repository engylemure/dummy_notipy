import { Portal } from "@headlessui/react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { useEffect } from "react";
import {
  getNotifications,
  notificationsPath,
  updateNotification,
  Notification,
} from "./api";

export default function Notifications({ userId }: { userId: number }) {
  const queryClient = useQueryClient();
  useEffect(() => {
    const queryKey = notificationsPath(userId);
    const websocket = new WebSocket(`ws://localhost:8081/${queryKey}-ws`);
    websocket.onmessage = function (ev) {
      queryClient.invalidateQueries({ queryKey: [queryKey] });
    };
    return () => {
      websocket.close();
    };
  }, [userId]);
  const query = useQuery({
    queryKey: [notificationsPath(userId)],
    queryFn: () => getNotifications(userId),
  });
  return (
    <Portal>
      <section className="fixed right-0 top-0 z-[51] grid gap-4 overflow-hidden px-2 pb-10 pt-4 md:p-10">
        <AnimatePresence>
          {query.data?.map((notification) => (
            <Notification
              key={`notification-${notification.id}`}
              {...notification}
              onClick={(notification) => {
                updateNotification({
                  ...notification,
                  viewed: !notification.viewed,
                });
              }}
              onClose={(notification) => {
                updateNotification({
                  ...notification,
                  deleted: true,
                });
              }}
            />
          ))}
        </AnimatePresence>
      </section>
    </Portal>
  );
}

function Notification({
  onClick,
  onClose,
  ...notification
}: Notification & {
  onClick: (notification: Notification) => void;
  onClose: (notfication: Notification) => void;
}) {
  const { id, content, viewed } = notification;
  return (
    <motion.div
      layout
      id={`notification-${id}`}
      onClick={() => onClick(notification)}
      initial={{ opacity: 0, left: "100%" }}
      animate={{ opacity: 1, left: "0" }}
      exit={{ opacity: 0, left: "100%" }}
      className="relative flex justify-between min-h-[64px] min-w-full rounded-lg bg-white shadow-notification md:min-w-[415px] max-w-[500px] flex-grow w-fit text-black px-4 py-4 transition-all hover:bg-gray-200 cursor-pointer"
    >
      <div
        className={`h-4 w-4 bg-red-400 rounded-full absolute top-[-0.5rem] right-[-0.5rem] transition-opacity	duration-300 ${
          !viewed ? "opacity-100" : "opacity-0"
        }`}
      />
      <p>{content}</p>
      <button
        className="bg-white border-1 border-black"
        onClick={() => onClose(notification)}
      >
        Close
      </button>
    </motion.div>
  );
}
