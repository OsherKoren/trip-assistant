import { useAuth } from '../hooks/useAuth';

export function LogoutButton() {
  const { signOut } = useAuth();

  return (
    <button
      onClick={signOut}
      aria-label="Sign out"
      className="rounded-md p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 min-h-[44px] min-w-[44px] flex items-center justify-center text-sm font-medium"
    >
      Sign Out
    </button>
  );
}
