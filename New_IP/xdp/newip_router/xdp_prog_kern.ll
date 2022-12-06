; ModuleID = 'xdp_prog_kern.c'
source_filename = "xdp_prog_kern.c"
target datalayout = "e-m:e-p:64:64-i64:64-i128:128-n32:64-S128"
target triple = "bpf"

%struct.bpf_map_def = type { i32, i32, i32, i32, i32 }
%struct.xdp_md = type { i32, i32, i32, i32, i32 }
%struct.bpf_fib_lookup = type { i8, i8, i16, i16, i16, i32, %union.anon, %union.anon.0, %union.anon.1, i16, i16, [6 x i8], [6 x i8] }
%union.anon = type { i32 }
%union.anon.0 = type { [4 x i32] }
%union.anon.1 = type { [4 x i32] }
%struct.ethhdr = type { [6 x i8], [6 x i8], i16 }
%struct.newip_offset = type { i8, i8, i8 }
%struct.shipping_spec = type { i8, i8, i8 }
%struct.meta_info = type { i32, %struct.max_delay_forwarding }
%struct.max_delay_forwarding = type { i16, i16, i16 }
%struct.in6_addr = type { %union.anon.2 }
%union.anon.2 = type { [4 x i32] }
%struct.ping_contract = type { i16, i16, i16, i64 }

@xdp_stats_map = dso_local global %struct.bpf_map_def { i32 6, i32 4, i32 16, i32 5, i32 0 }, section "maps", align 4
@static_redirect_8b = dso_local global %struct.bpf_map_def { i32 1, i32 1, i32 4, i32 256, i32 0 }, section "maps", align 4
@__const.xdp_router_func.____fmt = private unnamed_addr constant [12 x i8] c"no ifindex\0A\00", align 1
@__const.xdp_router_func.____fmt.1 = private unnamed_addr constant [60 x i8] c"route not found, check if routing suite is working properly\00", align 1
@_license = dso_local global [4 x i8] c"GPL\00", section "license", align 1
@llvm.compiler.used = appending global [5 x i8*] [i8* getelementptr inbounds ([4 x i8], [4 x i8]* @_license, i32 0, i32 0), i8* bitcast (%struct.bpf_map_def* @static_redirect_8b to i8*), i8* bitcast (i32 (%struct.xdp_md*)* @xdp_pass_func to i8*), i8* bitcast (i32 (%struct.xdp_md*)* @xdp_router_func to i8*), i8* bitcast (%struct.bpf_map_def* @xdp_stats_map to i8*)], section "llvm.metadata"

; Function Attrs: nounwind
define dso_local i32 @xdp_router_func(%struct.xdp_md* %0) #0 section "xdp_router" {
  %2 = alloca i32, align 4
  %3 = alloca %struct.bpf_fib_lookup, align 4
  %4 = alloca [12 x i8], align 1
  %5 = alloca [60 x i8], align 1
  %6 = tail call i64 inttoptr (i64 54 to i64 (%struct.xdp_md*, i32)*)(%struct.xdp_md* %0, i32 -12) #6
  %7 = trunc i64 %6 to i32
  %8 = icmp slt i32 %7, 0
  br i1 %8, label %172, label %9

9:                                                ; preds = %1
  %10 = getelementptr inbounds %struct.xdp_md, %struct.xdp_md* %0, i64 0, i32 1
  %11 = load i32, i32* %10, align 4, !tbaa !3
  %12 = zext i32 %11 to i64
  %13 = inttoptr i64 %12 to i8*
  %14 = getelementptr inbounds %struct.xdp_md, %struct.xdp_md* %0, i64 0, i32 0
  %15 = load i32, i32* %14, align 4, !tbaa !8
  %16 = zext i32 %15 to i64
  %17 = inttoptr i64 %16 to i8*
  %18 = getelementptr inbounds %struct.bpf_fib_lookup, %struct.bpf_fib_lookup* %3, i64 0, i32 0
  call void @llvm.lifetime.start.p0i8(i64 64, i8* nonnull %18) #6
  call void @llvm.memset.p0i8.i64(i8* noundef nonnull align 4 dereferenceable(64) %18, i8 0, i64 64, i1 false)
  %19 = inttoptr i64 %16 to %struct.ethhdr*
  %20 = getelementptr i8, i8* %17, i64 14
  %21 = icmp ugt i8* %20, %13
  br i1 %21, label %150, label %22

22:                                               ; preds = %9
  %23 = getelementptr inbounds %struct.ethhdr, %struct.ethhdr* %19, i64 0, i32 2
  %24 = load i16, i16* %23, align 1, !tbaa !9
  %25 = icmp eq i16 %24, -18808
  br i1 %25, label %26, label %150

26:                                               ; preds = %22
  %27 = getelementptr i8, i8* %17, i64 17
  %28 = bitcast i8* %27 to %struct.newip_offset*
  %29 = inttoptr i64 %12 to %struct.newip_offset*
  %30 = icmp ugt %struct.newip_offset* %28, %29
  br i1 %30, label %150, label %31

31:                                               ; preds = %26
  %32 = load i8, i8* %20, align 1, !tbaa !12
  %33 = zext i8 %32 to i64
  %34 = getelementptr i8, i8* %20, i64 %33
  %35 = getelementptr inbounds i8, i8* %34, i64 3
  %36 = bitcast i8* %35 to %struct.shipping_spec*
  %37 = inttoptr i64 %12 to %struct.shipping_spec*
  %38 = icmp ugt %struct.shipping_spec* %36, %37
  br i1 %38, label %150, label %39

39:                                               ; preds = %31
  %40 = getelementptr inbounds %struct.xdp_md, %struct.xdp_md* %0, i64 0, i32 2
  %41 = load i32, i32* %40, align 4, !tbaa !14
  %42 = zext i32 %41 to i64
  %43 = inttoptr i64 %42 to %struct.meta_info*
  %44 = getelementptr inbounds %struct.meta_info, %struct.meta_info* %43, i64 1
  %45 = inttoptr i64 %16 to %struct.meta_info*
  %46 = icmp ugt %struct.meta_info* %44, %45
  br i1 %46, label %170, label %47

47:                                               ; preds = %39
  %48 = load i8, i8* %34, align 1, !tbaa !15
  switch i8 %48, label %51 [
    i8 0, label %52
    i8 1, label %49
    i8 2, label %50
  ]

49:                                               ; preds = %47
  br label %52

50:                                               ; preds = %47
  br label %52

51:                                               ; preds = %47
  br label %52

52:                                               ; preds = %47, %51, %49, %50
  %53 = phi i64 [ 36, %49 ], [ 21, %50 ], [ 24, %47 ], [ 20, %51 ]
  %54 = getelementptr inbounds i8, i8* %34, i64 1
  %55 = load i8, i8* %54, align 1, !tbaa !17
  switch i8 %55, label %150 [
    i8 0, label %56
    i8 1, label %66
    i8 2, label %75
  ]

56:                                               ; preds = %52
  %57 = getelementptr i8, i8* %17, i64 %53
  %58 = getelementptr inbounds i8, i8* %57, i64 4
  %59 = bitcast i8* %58 to i32*
  %60 = inttoptr i64 %12 to i32*
  %61 = icmp ugt i32* %59, %60
  br i1 %61, label %150, label %62

62:                                               ; preds = %56
  %63 = bitcast i8* %57 to i32*
  store i8 2, i8* %18, align 4, !tbaa !18
  %64 = load i32, i32* %63, align 4, !tbaa !20
  %65 = getelementptr inbounds %struct.bpf_fib_lookup, %struct.bpf_fib_lookup* %3, i64 0, i32 8, i32 0, i64 0
  store i32 %64, i32* %65, align 4, !tbaa !21
  br label %89

66:                                               ; preds = %52
  %67 = getelementptr i8, i8* %17, i64 %53
  %68 = getelementptr inbounds i8, i8* %67, i64 16
  %69 = bitcast i8* %68 to %struct.in6_addr*
  %70 = inttoptr i64 %12 to %struct.in6_addr*
  %71 = icmp ugt %struct.in6_addr* %69, %70
  br i1 %71, label %150, label %72

72:                                               ; preds = %66
  %73 = getelementptr inbounds %struct.bpf_fib_lookup, %struct.bpf_fib_lookup* %3, i64 0, i32 8, i32 0, i64 0
  store i8 10, i8* %18, align 4, !tbaa !18
  %74 = bitcast i32* %73 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 4 dereferenceable(16) %74, i8* noundef nonnull align 4 dereferenceable(16) %67, i64 16, i1 false), !tbaa.struct !22
  br label %89

75:                                               ; preds = %52
  %76 = getelementptr i8, i8* %17, i64 %53
  %77 = getelementptr inbounds i8, i8* %76, i64 1
  %78 = icmp ugt i8* %77, %13
  br i1 %78, label %150, label %79

79:                                               ; preds = %75
  %80 = tail call i8* inttoptr (i64 1 to i8* (i8*, i8*)*)(i8* bitcast (%struct.bpf_map_def* @static_redirect_8b to i8*), i8* %76) #6
  %81 = icmp eq i8* %80, null
  br i1 %81, label %82, label %85

82:                                               ; preds = %79
  %83 = getelementptr inbounds [12 x i8], [12 x i8]* %4, i64 0, i64 0
  call void @llvm.lifetime.start.p0i8(i64 12, i8* nonnull %83) #6
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 1 dereferenceable(12) %83, i8* noundef nonnull align 1 dereferenceable(12) getelementptr inbounds ([12 x i8], [12 x i8]* @__const.xdp_router_func.____fmt, i64 0, i64 0), i64 12, i1 false)
  %84 = call i64 (i8*, i32, ...) inttoptr (i64 6 to i64 (i8*, i32, ...)*)(i8* nonnull %83, i32 12) #6
  call void @llvm.lifetime.end.p0i8(i64 12, i8* nonnull %83) #6
  br label %170

85:                                               ; preds = %79
  %86 = bitcast i8* %80 to i32*
  %87 = load i32, i32* %86, align 4, !tbaa !20
  %88 = getelementptr inbounds %struct.meta_info, %struct.meta_info* %43, i64 0, i32 0
  store i32 %87, i32* %88, align 4, !tbaa !23
  br label %89

89:                                               ; preds = %85, %72, %62
  %90 = getelementptr i8, i8* %17, i64 15
  %91 = load i8, i8* %90, align 1, !tbaa !26
  %92 = getelementptr i8, i8* %17, i64 16
  %93 = load i8, i8* %92, align 1, !tbaa !27
  %94 = icmp ult i8 %91, %93
  br i1 %94, label %95, label %130

95:                                               ; preds = %89
  %96 = zext i8 %91 to i64
  %97 = getelementptr i8, i8* %20, i64 %96
  %98 = getelementptr inbounds i8, i8* %97, i64 2
  %99 = bitcast i8* %98 to i16*
  %100 = inttoptr i64 %12 to i16*
  %101 = icmp ugt i16* %99, %100
  br i1 %101, label %150, label %102

102:                                              ; preds = %95
  %103 = bitcast i8* %97 to i16*
  %104 = load i16, i16* %103, align 2, !tbaa !28
  %105 = tail call i16 @llvm.bswap.i16(i16 %104)
  switch i16 %105, label %130 [
    i16 3, label %106
    i16 1, label %118
  ]

106:                                              ; preds = %102
  %107 = getelementptr inbounds i8, i8* %97, i64 16
  %108 = bitcast i8* %107 to %struct.ping_contract*
  %109 = inttoptr i64 %12 to %struct.ping_contract*
  %110 = icmp ugt %struct.ping_contract* %108, %109
  br i1 %110, label %150, label %111

111:                                              ; preds = %106
  %112 = getelementptr inbounds i8, i8* %97, i64 4
  %113 = bitcast i8* %112 to i16*
  %114 = load i16, i16* %113, align 4, !tbaa !29
  %115 = tail call i16 @llvm.bswap.i16(i16 %114)
  %116 = add i16 %115, -1
  %117 = tail call i16 @llvm.bswap.i16(i16 %116)
  store i16 %117, i16* %113, align 4, !tbaa !29
  br label %130

118:                                              ; preds = %102
  %119 = getelementptr inbounds i8, i8* %97, i64 6
  %120 = bitcast i8* %119 to %struct.max_delay_forwarding*
  %121 = inttoptr i64 %12 to %struct.max_delay_forwarding*
  %122 = icmp ugt %struct.max_delay_forwarding* %120, %121
  br i1 %122, label %150, label %123

123:                                              ; preds = %118
  %124 = load i16, i16* %99, align 2, !tbaa !32
  %125 = getelementptr inbounds %struct.meta_info, %struct.meta_info* %43, i64 0, i32 1, i32 1
  store i16 %124, i16* %125, align 2, !tbaa !33
  %126 = getelementptr inbounds i8, i8* %97, i64 4
  %127 = bitcast i8* %126 to i16*
  %128 = load i16, i16* %127, align 2, !tbaa !34
  %129 = getelementptr inbounds %struct.meta_info, %struct.meta_info* %43, i64 0, i32 1, i32 2
  store i16 %128, i16* %129, align 4, !tbaa !35
  br label %130

130:                                              ; preds = %102, %111, %123, %89
  %131 = icmp eq i8 %55, 2
  br i1 %131, label %150, label %132

132:                                              ; preds = %130
  %133 = getelementptr inbounds %struct.xdp_md, %struct.xdp_md* %0, i64 0, i32 3
  %134 = load i32, i32* %133, align 4, !tbaa !36
  %135 = getelementptr inbounds %struct.bpf_fib_lookup, %struct.bpf_fib_lookup* %3, i64 0, i32 5
  store i32 %134, i32* %135, align 4, !tbaa !37
  %136 = bitcast %struct.xdp_md* %0 to i8*
  %137 = call i64 inttoptr (i64 69 to i64 (i8*, %struct.bpf_fib_lookup*, i32, i32)*)(i8* %136, %struct.bpf_fib_lookup* nonnull %3, i32 64, i32 0) #6
  %138 = trunc i64 %137 to i32
  switch i32 %138, label %150 [
    i32 0, label %139
    i32 1, label %146
    i32 2, label %146
    i32 3, label %146
    i32 4, label %147
  ]

139:                                              ; preds = %132
  %140 = getelementptr inbounds %struct.ethhdr, %struct.ethhdr* %19, i64 0, i32 0, i64 0
  %141 = getelementptr inbounds %struct.bpf_fib_lookup, %struct.bpf_fib_lookup* %3, i64 0, i32 12, i64 0
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 1 dereferenceable(6) %140, i8* noundef nonnull align 2 dereferenceable(6) %141, i64 6, i1 false)
  %142 = getelementptr inbounds %struct.ethhdr, %struct.ethhdr* %19, i64 0, i32 1, i64 0
  %143 = getelementptr inbounds %struct.bpf_fib_lookup, %struct.bpf_fib_lookup* %3, i64 0, i32 11, i64 0
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 1 dereferenceable(6) %142, i8* noundef nonnull align 4 dereferenceable(6) %143, i64 6, i1 false)
  %144 = load i32, i32* %135, align 4, !tbaa !37
  %145 = getelementptr inbounds %struct.meta_info, %struct.meta_info* %43, i64 0, i32 0
  store i32 %144, i32* %145, align 4, !tbaa !23
  br label %150

146:                                              ; preds = %132, %132, %132
  br label %150

147:                                              ; preds = %132
  %148 = getelementptr inbounds [60 x i8], [60 x i8]* %5, i64 0, i64 0
  call void @llvm.lifetime.start.p0i8(i64 60, i8* nonnull %148) #6
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 1 dereferenceable(60) %148, i8* noundef nonnull align 1 dereferenceable(60) getelementptr inbounds ([60 x i8], [60 x i8]* @__const.xdp_router_func.____fmt.1, i64 0, i64 0), i64 60, i1 false)
  %149 = call i64 (i8*, i32, ...) inttoptr (i64 6 to i64 (i8*, i32, ...)*)(i8* nonnull %148, i32 60) #6
  call void @llvm.lifetime.end.p0i8(i64 60, i8* nonnull %148) #6
  br label %150

150:                                              ; preds = %130, %118, %106, %66, %56, %95, %52, %75, %31, %26, %9, %139, %146, %132, %147, %22
  %151 = phi i32 [ 2, %132 ], [ 2, %147 ], [ 1, %146 ], [ 2, %139 ], [ 2, %22 ], [ 1, %9 ], [ 1, %26 ], [ 1, %31 ], [ 1, %75 ], [ 1, %95 ], [ 1, %52 ], [ 1, %56 ], [ 1, %66 ], [ 1, %106 ], [ 1, %118 ], [ 2, %130 ]
  %152 = bitcast i32* %2 to i8*
  call void @llvm.lifetime.start.p0i8(i64 4, i8* nonnull %152)
  store i32 %151, i32* %2, align 4, !tbaa !20
  %153 = call i8* inttoptr (i64 1 to i8* (i8*, i8*)*)(i8* bitcast (%struct.bpf_map_def* @xdp_stats_map to i8*), i8* nonnull %152) #6
  %154 = icmp eq i8* %153, null
  br i1 %154, label %168, label %155

155:                                              ; preds = %150
  %156 = bitcast i8* %153 to i64*
  %157 = load i64, i64* %156, align 8, !tbaa !38
  %158 = add i64 %157, 1
  store i64 %158, i64* %156, align 8, !tbaa !38
  %159 = load i32, i32* %10, align 4, !tbaa !3
  %160 = load i32, i32* %14, align 4, !tbaa !8
  %161 = sub i32 %159, %160
  %162 = zext i32 %161 to i64
  %163 = getelementptr inbounds i8, i8* %153, i64 8
  %164 = bitcast i8* %163 to i64*
  %165 = load i64, i64* %164, align 8, !tbaa !40
  %166 = add i64 %165, %162
  store i64 %166, i64* %164, align 8, !tbaa !40
  %167 = load i32, i32* %2, align 4, !tbaa !20
  br label %168

168:                                              ; preds = %150, %155
  %169 = phi i32 [ %167, %155 ], [ 0, %150 ]
  call void @llvm.lifetime.end.p0i8(i64 4, i8* nonnull %152)
  br label %170

170:                                              ; preds = %82, %39, %168
  %171 = phi i32 [ %169, %168 ], [ 0, %39 ], [ 0, %82 ]
  call void @llvm.lifetime.end.p0i8(i64 64, i8* nonnull %18) #6
  br label %172

172:                                              ; preds = %1, %170
  %173 = phi i32 [ %171, %170 ], [ 0, %1 ]
  ret i32 %173
}

; Function Attrs: argmemonly mustprogress nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #1

; Function Attrs: argmemonly mustprogress nofree nounwind willreturn writeonly
declare void @llvm.memset.p0i8.i64(i8* nocapture writeonly, i8, i64, i1 immarg) #2

; Function Attrs: argmemonly mustprogress nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #1

; Function Attrs: argmemonly mustprogress nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #3

; Function Attrs: mustprogress nofree nosync nounwind readnone speculatable willreturn
declare i16 @llvm.bswap.i16(i16) #4

; Function Attrs: mustprogress nofree norecurse nosync nounwind readnone willreturn
define dso_local i32 @xdp_pass_func(%struct.xdp_md* nocapture readnone %0) #5 section "xdp_pass" {
  ret i32 2
}

attributes #0 = { nounwind "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" }
attributes #1 = { argmemonly mustprogress nofree nosync nounwind willreturn }
attributes #2 = { argmemonly mustprogress nofree nounwind willreturn writeonly }
attributes #3 = { argmemonly mustprogress nofree nounwind willreturn }
attributes #4 = { mustprogress nofree nosync nounwind readnone speculatable willreturn }
attributes #5 = { mustprogress nofree norecurse nosync nounwind readnone willreturn "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" }
attributes #6 = { nounwind }

!llvm.module.flags = !{!0, !1}
!llvm.ident = !{!2}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"frame-pointer", i32 2}
!2 = !{!"Ubuntu clang version 13.0.0-2"}
!3 = !{!4, !5, i64 4}
!4 = !{!"xdp_md", !5, i64 0, !5, i64 4, !5, i64 8, !5, i64 12, !5, i64 16}
!5 = !{!"int", !6, i64 0}
!6 = !{!"omnipotent char", !7, i64 0}
!7 = !{!"Simple C/C++ TBAA"}
!8 = !{!4, !5, i64 0}
!9 = !{!10, !11, i64 12}
!10 = !{!"ethhdr", !6, i64 0, !6, i64 6, !11, i64 12}
!11 = !{!"short", !6, i64 0}
!12 = !{!13, !6, i64 0}
!13 = !{!"newip_offset", !6, i64 0, !6, i64 1, !6, i64 2}
!14 = !{!4, !5, i64 8}
!15 = !{!16, !6, i64 0}
!16 = !{!"shipping_spec", !6, i64 0, !6, i64 1, !6, i64 2}
!17 = !{!16, !6, i64 1}
!18 = !{!19, !6, i64 0}
!19 = !{!"bpf_fib_lookup", !6, i64 0, !6, i64 1, !11, i64 2, !11, i64 4, !11, i64 6, !5, i64 8, !6, i64 12, !6, i64 16, !6, i64 32, !11, i64 48, !11, i64 50, !6, i64 52, !6, i64 58}
!20 = !{!5, !5, i64 0}
!21 = !{!6, !6, i64 0}
!22 = !{i64 0, i64 16, !21, i64 0, i64 16, !21, i64 0, i64 16, !21}
!23 = !{!24, !5, i64 0}
!24 = !{!"meta_info", !5, i64 0, !25, i64 4}
!25 = !{!"max_delay_forwarding", !11, i64 0, !11, i64 2, !11, i64 4}
!26 = !{!13, !6, i64 1}
!27 = !{!13, !6, i64 2}
!28 = !{!11, !11, i64 0}
!29 = !{!30, !11, i64 4}
!30 = !{!"ping_contract", !11, i64 0, !11, i64 2, !11, i64 4, !31, i64 8}
!31 = !{!"long long", !6, i64 0}
!32 = !{!25, !11, i64 2}
!33 = !{!24, !11, i64 6}
!34 = !{!25, !11, i64 4}
!35 = !{!24, !11, i64 8}
!36 = !{!4, !5, i64 12}
!37 = !{!19, !5, i64 8}
!38 = !{!39, !31, i64 0}
!39 = !{!"datarec", !31, i64 0, !31, i64 8}
!40 = !{!39, !31, i64 8}
