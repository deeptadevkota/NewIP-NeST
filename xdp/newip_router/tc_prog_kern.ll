; ModuleID = 'tc_prog_kern.c'
source_filename = "tc_prog_kern.c"
target datalayout = "e-m:e-p:64:64-i64:64-i128:128-n32:64-S128"
target triple = "bpf"

%struct.__sk_buff = type { i32, i32, i32, i32, i32, i32, i32, i32, i32, i32, i32, i32, [5 x i32], i32, i32, i32, i32, i32, i32, i32, i32, [4 x i32], [4 x i32], i32, i32, i32, %union.anon, i64, i32, i32, %union.anon.2 }
%union.anon = type { %struct.bpf_flow_keys* }
%struct.bpf_flow_keys = type { i16, i16, i16, i8, i8, i8, i8, i16, i16, i16, %union.anon.0 }
%union.anon.0 = type { %struct.anon.1 }
%struct.anon.1 = type { [4 x i32], [4 x i32] }
%union.anon.2 = type { %struct.bpf_sock* }
%struct.bpf_sock = type { i32, i32, i32, i32, i32, i32, i32, [4 x i32], i32, i32, i32, [4 x i32], i32 }
%struct.meta_info = type { i32, %struct.max_delay_forwarding }
%struct.max_delay_forwarding = type { i16, i16, i16 }
%struct.ethhdr = type { [6 x i8], [6 x i8], i16 }

@_license = dso_local global [4 x i8] c"GPL\00", section "license", align 1
@llvm.compiler.used = appending global [2 x i8*] [i8* getelementptr inbounds ([4 x i8], [4 x i8]* @_license, i32 0, i32 0), i8* bitcast (i32 (%struct.__sk_buff*)* @tc_router_func to i8*)], section "llvm.metadata"

; Function Attrs: nounwind
define dso_local i32 @tc_router_func(%struct.__sk_buff* nocapture %0) #0 section "tc_router" {
  %2 = getelementptr inbounds %struct.__sk_buff, %struct.__sk_buff* %0, i64 0, i32 15
  %3 = load i32, i32* %2, align 4, !tbaa !3
  %4 = zext i32 %3 to i64
  %5 = inttoptr i64 %4 to i8*
  %6 = getelementptr inbounds %struct.__sk_buff, %struct.__sk_buff* %0, i64 0, i32 16
  %7 = load i32, i32* %6, align 8, !tbaa !9
  %8 = zext i32 %7 to i64
  %9 = inttoptr i64 %8 to i8*
  %10 = getelementptr inbounds %struct.__sk_buff, %struct.__sk_buff* %0, i64 0, i32 25
  %11 = load i32, i32* %10, align 4, !tbaa !10
  %12 = zext i32 %11 to i64
  %13 = inttoptr i64 %12 to %struct.meta_info*
  %14 = getelementptr i8, i8* %5, i64 14
  %15 = icmp ugt i8* %14, %9
  br i1 %15, label %30, label %16

16:                                               ; preds = %1
  %17 = inttoptr i64 %4 to %struct.ethhdr*
  %18 = getelementptr inbounds %struct.ethhdr, %struct.ethhdr* %17, i64 0, i32 2
  %19 = load i16, i16* %18, align 1, !tbaa !11
  %20 = icmp eq i16 %19, -18808
  br i1 %20, label %21, label %30

21:                                               ; preds = %16
  %22 = getelementptr inbounds %struct.meta_info, %struct.meta_info* %13, i64 1
  %23 = inttoptr i64 %4 to %struct.meta_info*
  %24 = icmp ugt %struct.meta_info* %22, %23
  br i1 %24, label %30, label %25

25:                                               ; preds = %21
  %26 = getelementptr inbounds %struct.meta_info, %struct.meta_info* %13, i64 0, i32 0
  %27 = load i32, i32* %26, align 4, !tbaa !14
  %28 = tail call i64 inttoptr (i64 23 to i64 (i32, i64)*)(i32 %27, i64 0) #1
  %29 = trunc i64 %28 to i32
  br label %30

30:                                               ; preds = %1, %21, %16, %25
  %31 = phi i32 [ -1, %16 ], [ -1, %21 ], [ %29, %25 ], [ 2, %1 ]
  %32 = getelementptr inbounds %struct.__sk_buff, %struct.__sk_buff* %0, i64 0, i32 12, i64 0
  store i32 65, i32* %32, align 4, !tbaa !17
  ret i32 %31
}

attributes #0 = { nounwind "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" }
attributes #1 = { nounwind }

!llvm.module.flags = !{!0, !1}
!llvm.ident = !{!2}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"frame-pointer", i32 2}
!2 = !{!"Ubuntu clang version 13.0.0-2"}
!3 = !{!4, !5, i64 76}
!4 = !{!"__sk_buff", !5, i64 0, !5, i64 4, !5, i64 8, !5, i64 12, !5, i64 16, !5, i64 20, !5, i64 24, !5, i64 28, !5, i64 32, !5, i64 36, !5, i64 40, !5, i64 44, !6, i64 48, !5, i64 68, !5, i64 72, !5, i64 76, !5, i64 80, !5, i64 84, !5, i64 88, !5, i64 92, !5, i64 96, !6, i64 100, !6, i64 116, !5, i64 132, !5, i64 136, !5, i64 140, !6, i64 144, !8, i64 152, !5, i64 160, !5, i64 164, !6, i64 168}
!5 = !{!"int", !6, i64 0}
!6 = !{!"omnipotent char", !7, i64 0}
!7 = !{!"Simple C/C++ TBAA"}
!8 = !{!"long long", !6, i64 0}
!9 = !{!4, !5, i64 80}
!10 = !{!4, !5, i64 140}
!11 = !{!12, !13, i64 12}
!12 = !{!"ethhdr", !6, i64 0, !6, i64 6, !13, i64 12}
!13 = !{!"short", !6, i64 0}
!14 = !{!15, !5, i64 0}
!15 = !{!"meta_info", !5, i64 0, !16, i64 4}
!16 = !{!"max_delay_forwarding", !13, i64 0, !13, i64 2, !13, i64 4}
!17 = !{!18, !5, i64 0}
!18 = !{!"lbf_skb_cb", !5, i64 0}
