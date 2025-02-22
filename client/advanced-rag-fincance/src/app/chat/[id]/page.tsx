export default async function Page({
  params
}: {
  params: Promise<{ id: "string" }>;
}) {
  const id = (await params).id;

  return (
    <div className="flex h-screen w-full items-center justify-center">{id}</div>
  );
}
