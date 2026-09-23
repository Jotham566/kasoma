import Link from "next/link";
export default function Notice() {
  return (
    <main className="mx-auto max-w-2xl p-6">
      <h1 className="text-3xl font-semibold my-6">
        Synthetic development notice
      </h1>
      <p className="my-4">
        This fixture tests the consent workflow. It is not an approved privacy
        notice or permission to enroll real learners.
      </p>
      <p className="my-4">
        Use fictional names, dates and contacts only. This local test stores
        your synthetic profile and versioned declarations. You can withdraw the
        declarations from the profile screen; learning authorization then stops.
      </p>
      <p className="my-4">
        Under-18 test profiles require a separately verified guardian
        declaration and learner assent. Adult test profiles require their own
        declaration. Verification checks contact possession.
      </p>
      <p className="my-4">
        Version: synthetic-development-v1. No external models or messaging
        services are used. Legal, privacy and safeguarding approval is required
        before real enrollment.
      </p>
      <Link
        href="/onboarding"
        className="underline inline-flex min-h-11 items-center"
      >
        Return to profile
      </Link>
    </main>
  );
}
