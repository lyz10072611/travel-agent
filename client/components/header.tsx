"use client";

import { Button } from "@/components/ui/button";
import Link from "next/link";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Luggage } from "lucide-react";

export default function Header() {
  const router = useRouter();
  const { data: session, isPending } = authClient.useSession();

  async function handleLogout() {
    try {
      await authClient.signOut();
      toast.success("已成功退出登录");
      router.push("/");
    } catch (error) {
      toast.error("退出登录失败");
      console.error("退出登录错误:", error);
    }
  }

  return (
    <header className="bg-card shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <div className="flex items-center gap-8">
            <Link href="/" className="hover:opacity-80 transition-opacity">
              <h1 className="text-2xl font-bold text-accent">TripCraft AI</h1>
            </Link>

            <nav className="flex items-center gap-6">
              <Link
                href="/plans"
                className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                <Luggage className="w-4 h-4" />
                我的计划
              </Link>
            </nav>
          </div>

          <div className="flex items-center gap-4">
            {isPending ? (
              <div className="text-sm text-muted-foreground">加载中...</div>
            ) : session?.user ? (
              <div className="flex items-center gap-4">
                <div className="text-sm">
                  <span className="text-muted-foreground">欢迎, </span>
                  <span className="font-medium">
                    {session.user.name || session.user.email}
                  </span>
                </div>
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  退出登录
                </Button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link href="/auth">
                  <Button variant="outline" size="sm">
                    登录
                  </Button>
                </Link>
                <Link href="/plan">
                  <Button className="bg-primary hover:bg-primary/90">
                    开始使用
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
