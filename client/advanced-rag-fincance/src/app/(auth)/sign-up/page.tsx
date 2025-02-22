import { GalleryVerticalEnd } from "lucide-react";

import SignUpForm from "./components/signup-form";

export default function LoginPage() {
  return (
    <div className="grid min-h-svh place-items-center">
      <div className="flex flex-col justify-center gap-4 p-6 md:p-10">
        <div className="flex justify-center gap-2">
          <a href="#" className="flex items-center gap-2 font-medium">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <GalleryVerticalEnd className="size-4" />
            </div>
          </a>
        </div>
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-md">
            <SignUpForm />
          </div>
        </div>
      </div>
    </div>
  );
}
