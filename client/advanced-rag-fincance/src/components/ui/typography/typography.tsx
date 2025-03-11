import React from "react";

interface TypographyProps {
  children: string;
}

export function TypographyH1({ children }: TypographyProps) {
  return (
    <h1 className="my-4 py-2 text-4xl font-extrabold tracking-tight lg:text-5xl">
      {children}
    </h1>
  );
}

export function TypographyH2({ children }: TypographyProps) {
  return (
    <h2 className="my-4 scroll-m-20 py-2 pb-2 text-3xl font-semibold tracking-tight first:mt-0">
      {children}
    </h2>
  );
}

export function TypographyH3({ children }: TypographyProps) {
  return (
    <h3 className="my-4 scroll-m-20 py-2 text-2xl font-semibold tracking-tight">
      {children}
    </h3>
  );
}

export function TypographyH4({ children }: TypographyProps) {
  return (
    <h4 className="my-4 scroll-m-20 py-2 text-xl font-semibold tracking-tight">
      {children}
    </h4>
  );
}

export function TypographyP({ children }: TypographyProps) {
  return <p className="my-4 py-2 leading-7">{children}</p>;
}

export function TypographyInlineCode({ children }: TypographyProps) {
  return (
    <code className="relative my-4 rounded bg-muted px-[0.3rem] py-2  font-mono text-sm font-semibold">
      {children}
    </code>
  );
}

export function TypographyList({ children }: TypographyProps) {
  return <ul className=" ml-6 list-disc [&>li]:mt-2 my-4 py-2">{children}</ul>;
}

export function TypographyListItem({ children }: TypographyProps) {
  return <li className="my-4 py-2">{children}</li>;
}

export function TypographyBlockquote({ children }: TypographyProps) {
  return (
    <blockquote className="my-4 mt-6 border-l-2 py-2 pl-6 italic">
      {children}
    </blockquote>
  );
}
