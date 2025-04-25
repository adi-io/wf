import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function InputFile() {
  return (
    <div className="grid w-full max-w-sm items-center gap-1.5">
      <Label htmlFor="master_fie">Zip file</Label>
      <Input id="master_filr" type="file" accept=".zip" />
    </div>
  );
}
