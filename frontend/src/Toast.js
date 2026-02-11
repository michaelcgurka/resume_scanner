import React, { useEffect } from "react";

/**
 * Small popup toast for success/notification messages.
 * Auto-dismisses after a delay.
 */
function Toast({ message, visible, onDismiss, duration = 4000 }) {
  useEffect(() => {
    if (!visible || !onDismiss) return;
    const id = setTimeout(onDismiss, duration);
    return () => clearTimeout(id);
  }, [visible, onDismiss, duration]);

  if (!visible || !message) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className="fixed bottom-6 left-1/2 z-50 animate-toast-in"
    >
      <div className="flex items-center gap-2 px-4 py-3 rounded-lg shadow-lg bg-teal-600 dark:bg-teal-700 text-white text-sm font-medium max-w-md">
        <svg
          className="flex-shrink-0 w-5 h-5 text-teal-200"
          fill="currentColor"
          viewBox="0 0 20 20"
          aria-hidden
        >
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
            clipRule="evenodd"
          />
        </svg>
        <span>{message}</span>
      </div>
    </div>
  );
}

export default Toast;
