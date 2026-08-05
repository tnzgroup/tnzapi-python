import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export type FieldValues = Record<string, string | boolean | undefined>;

type TextFieldProps = {
  label: string;
  name: string;
  values: FieldValues;
  onChange: (name: string, value: string) => void;
  multiline?: boolean;
  placeholder?: string;
  disabled?: boolean;
  // Defaults to `name`. A page that renders two TextFields for the same field name at once (e.g.
  // a Create form and an Edit form both with a "FirstName" field, as in ContactsPage) must pass a
  // distinct id for one of them — otherwise both render <input id="FirstName">, which is invalid
  // HTML and breaks label association (a browser/assistive tech resolves a duplicate id
  // ambiguously, and so does React Testing Library's getByLabelText).
  id?: string;
};

export function TextField({ label, name, values, onChange, multiline, placeholder, disabled, id }: TextFieldProps) {
  const value = (values[name] as string) ?? "";
  const fieldId = id ?? name;
  return (
    <div className="space-y-1">
      <Label htmlFor={fieldId}>{label}</Label>
      {multiline ? (
        <Textarea
          id={fieldId}
          value={value}
          placeholder={placeholder}
          onChange={(e) => onChange(name, e.target.value)}
          rows={3}
          disabled={disabled}
        />
      ) : (
        <Input
          id={fieldId}
          value={value}
          placeholder={placeholder}
          onChange={(e) => onChange(name, e.target.value)}
          disabled={disabled}
        />
      )}
    </div>
  );
}

type SelectFieldProps = {
  label: string;
  name: string;
  values: FieldValues;
  onChange: (name: string, value: string) => void;
  options: string[];
  placeholder?: string;
  // Defaults to `name` — see TextField's `id` doc comment for why a page rendering two SelectFields
  // for the same field name at once needs to pass a distinct one.
  id?: string;
};

export function SelectField({ label, name, values, onChange, options, placeholder, id }: SelectFieldProps) {
  const value: string = (values[name] as string | undefined) ?? "";
  const fieldId = id ?? name;
  return (
    <div className="space-y-1">
      <Label htmlFor={fieldId}>{label}</Label>
      <Select value={value} onValueChange={(v) => v !== null && onChange(name, v)}>
        <SelectTrigger id={fieldId}>
          <SelectValue placeholder={placeholder ?? "(none)"} />
        </SelectTrigger>
        <SelectContent>
          {options.map((opt) => (
            <SelectItem key={opt} value={opt}>
              {opt}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

type CheckboxFieldProps = {
  label: string;
  name: string;
  values: FieldValues;
  onChange: (name: string, value: boolean) => void;
  // Defaults to `name` — see TextField's `id` doc comment for why a page rendering two CheckboxFields
  // for the same field name at once needs to pass a distinct one.
  id?: string;
};

export function CheckboxField({ label, name, values, onChange, id }: CheckboxFieldProps) {
  const checked = Boolean(values[name]);
  const fieldId = id ?? name;
  return (
    <div className="flex items-center gap-2">
      <input
        id={fieldId}
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(name, e.target.checked)}
      />
      <Label htmlFor={fieldId}>{label}</Label>
    </div>
  );
}