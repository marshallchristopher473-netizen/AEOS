import { redirect } from 'next/navigation';

export default function HomePage() {
  // The application root had no route, so the deployed base URL returned 404.
  // Send pilot users to the sign-in entry point; it forwards an already
  // authenticated user on to their students.
  redirect('/login');
}
