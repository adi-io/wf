import Image from "next/image";
import { InputFile } from "@/components/ui/upload";
import { InputForm } from "@/components/ui/upload2";

export default function Home() {
  return (
    <div className="w-2/3 space-y-6">
      <InputFile />
      <InputForm></InputForm>
    </div>
  );
}
