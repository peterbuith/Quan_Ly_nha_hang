import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. Cấu hình trang web
st.set_page_config(page_title="Hệ Thống Quản Lý Gọi Món & Doanh Thu", page_icon="🍔", layout="wide")

# Các file lưu trữ dữ liệu local
DATA_ORDER = "danh_sach_order.csv"         # Lưu các món đang ăn tại bàn
DATA_HISTORY = "lich_su_thanh_toan.csv"     # Lưu lịch sử các hóa đơn đã tính tiền

# Danh sách 10 món ăn cố định (Menu) kèm Emoji
MENU = {
    "Nước mía": 10000,
    "Nước dừa tươi": 15000,
    "Nước ngọt các loại": 15000,
    "Sting": 20000,
    "Bò Hút": 30000,
    "Cam vắt": 15000,
    "Nước ép trái cây": 35000,
    "Cà Phê Sữa Đá": 20000,
    "Mì gói": 15000,
    "Mì trứng gà": 20000
}

# --- HÀM XỬ LÝ DỮ LIỆU ---
def load_data(file_name, columns):
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    else:
        return pd.DataFrame(columns=columns)

def save_data(df, file_name):
    df.to_csv(file_name, index=False)

# Tải dữ liệu từ máy tính lên hệ thống
df_orders = load_data(DATA_ORDER, ["Bàn", "Món Ăn", "Giá", "Số Lượng", "Thành Tiền"])
df_history = load_data(DATA_HISTORY, ["Thời Gian", "Bàn", "Món Ăn", "Giá", "Số Lượng", "Thành Tiền"])

# --- KHỞI TẠO BỘ NHỚ TẠM CHO BÀN ĐANG ĐƯỢC CHỌN TRỰC TIẾP ---
if "ban_dang_chon" not in st.session_state:
    st.session_state["ban_dang_chon"] = "Bàn Số 1" # Mặc định ban đầu chọn Bàn 1

# --- MENU ĐIỀU HƯỚNG TẠI SIDEBAR ---
st.sidebar.title("🎛️ BẢNG ĐIỀU KHIỂN")
chức_năng = st.sidebar.radio("Chọn chức năng quản lý:", ["🍕 Gọi Món & Bán Hàng", "📊 Thống Kê & Xuất Dữ Liệu"])

# ==============================================================================
# TRANG 1: GIAO DIỆN GỌI MÓN VÀ BÁN HÀNG
# ==============================================================================
if chức_năng == "🍕 Gọi Món & Bán Hàng":
    st.title("🍕 HỆ THỐNG GIẢ LẬP ORDER & QUẢN LÝ QUÁN GIẾNG GIACOB")
    st.write(f"👉 Mẹo: Bấm trực tiếp vào danh sách bàn ở Cột 1 để xem thông tin bàn đó. Bạn đang xem: **{st.session_state['ban_dang_chon']}**")

    # Chia màn hình làm 3 phần: Khu vực Bàn (Trái), Khu vực Gọi món (Giữa), Khu vực Hóa đơn (Phải)
    col_ban, col_menu, col_bill = st.columns([1, 1.4, 1.6])

    # ----------------- KHU VỰC 1: SƠ ĐỒ 10 BÀN THÔNG MINH -----------------
    with col_ban:
        st.header("🪑 Sơ Đồ 10 Bàn")
        st.write("*(Bấm vào nút để chọn bàn)*")
        
        for i in range(1, 11):
            ten_ban = f"Bàn Số {i}"
            order_cua_ban = df_orders[df_orders["Bàn"] == ten_ban]
            
            # Tính toán trạng thái bàn để hiển thị chữ trên nút bấm
            if not order_cua_ban.empty:
                tong_tien_ban = order_cua_ban["Thành Tiền"].sum()
                nhãn_nút = f"🔴 {ten_ban} ({tong_tien_ban:,.0f} đ)"
            else:
                nhãn_nút = f"🟢 {ten_ban} (Trống)"
            
            # Đổi màu viền nút nếu bàn đó đang được click chọn xem thông tin
            đang_chọn = "primary" if st.session_state["ban_dang_chon"] == ten_ban else "secondary"
            
            # Tạo nút bấm đại diện cho bàn ăn
            if st.button(nhãn_nút, key=f"btn_ban_{i}", use_container_width=True, type=đang_chọn):
                st.session_state["ban_dang_chon"] = ten_ban # Cập nhật bàn đang chọn khi click
                st.rerun()

    # ----------------- KHU VỰC 2: MENU & GỌI MÓN THEO BÀN ĐÃ CHỌN -----------------
    with col_menu:
        ban_chon = st.session_state["ban_dang_chon"] # Lấy dữ liệu bàn từ Khu vực 1 qua
        
        st.header(f"📜 Gọi Món: {ban_chon}")
        st.write(f"Đang tiến hành đặt món cho **{ban_chon}**")
        
        with st.form(key="menu_order_form", clear_on_submit=True):
            danh_sach_chon_mon = {}
            for index, (mon_an, gia_tien) in enumerate(MENU.items()):
                c1, c2 = st.columns([2, 1])
                with c1:
                    da_chon = st.checkbox(f"**{mon_an}** ({gia_tien:,.0f} đ)", key=f"form_chk_{mon_an}")
                with c2:
                    so_luong = st.number_input("Số lượng:", min_value=0, max_value=20, value=0, step=1, key=f"form_num_{mon_an}")
                    if da_chon and so_luong > 0:
                        danh_sach_chon_mon[mon_an] = so_luong

            st.write("")
            btn_dat_mon = st.form_submit_button(f"🔥 XÁC NHẬN GỬI BẾP ({ban_chon.upper()})", use_container_width=True, type="primary")
            
            if btn_dat_mon:
                if len(danh_sach_chon_mon) > 0:
                    for mon_an, so_luong in danh_sach_chon_mon.items():
                        gia_mon = MENU[mon_an]
                        thanh_tien = gia_mon * so_luong
                        
                        dieu_kien = (df_orders["Bàn"] == ban_chon) & (df_orders["Món Ăn"] == mon_an)
                        if any(dieu_kien):
                            df_orders.loc[dieu_kien, "Số Lượng"] += so_luong
                            df_orders.loc[dieu_kien, "Thành Tiền"] = df_orders.loc[dieu_kien, "Số Lượng"] * gia_mon
                        else:
                            new_item = pd.DataFrame([{"Bàn": ban_chon, "Món Ăn": mon_an, "Giá": gia_mon, "Số Lượng": so_luong, "Thành Tiền": thanh_tien}])
                            df_orders = pd.concat([df_orders, new_item], ignore_index=True)
                    
                    save_data(df_orders, DATA_ORDER)
                    st.success(f"✔️ Đã đặt món thành công cho {ban_chon}!")
                    st.rerun()
                else:
                    st.warning("⚠️ Bạn chưa tick chọn món hoặc chưa nhập số lượng!")

    # ------ KHU VỰC 3: CHI TIẾT ĐƠN HÀNG, SỬA/HỦY & BIÊN LAI CỦA BÀN ĐÃ CHỌN ------
    with col_bill:
        ban_xem_bill = st.session_state["ban_dang_chon"] # Đồng bộ tự động theo Khu vực 1
        
        st.header(f"🧾 Hóa Đơn: {ban_xem_bill}")
        bill_ban = df_orders[df_orders["Bàn"] == ban_xem_bill]
        
        if not bill_ban.empty:
            st.write(f"Danh sách món hiện tại:")
            st.dataframe(bill_ban[["Món Ăn", "Giá", "Số Lượng", "Thành Tiền"]], use_container_width=True, hide_index=True)
            
            tong_bill = bill_ban["Thành Tiền"].sum()
            st.markdown(f"## 💰 TỔNG CỘNG: `{tong_bill:,.0f} VND`")
            
            # Khối chỉnh sửa/Hủy món
            with st.expander("🛠️ Chỉnh Sửa / Hủy Món"):
                mon_can_sua = st.selectbox("Chọn món muốn Thay đổi/Hủy:", list(bill_ban["Món Ăn"].values))
                so_luong_hien_tai = int(bill_ban[bill_ban["Món Ăn"] == mon_can_sua]["Số Lượng"].values[0])
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    so_luong_moi = st.number_input("Nhập số lượng mới:", min_value=1, max_value=50, value=so_luong_hien_tai, step=1)
                    if st.button("🔄 Cập Nhật Số Lượng", use_container_width=True):
                        dieu_kien_sua = (df_orders["Bàn"] == ban_xem_bill) & (df_orders["Món Ăn"] == mon_can_sua)
                        df_orders.loc[dieu_kien_sua, "Số Lượng"] = so_luong_moi
                        df_orders.loc[dieu_kien_sua, "Thành Tiền"] = so_luong_moi * MENU[mon_can_sua]
                        save_data(df_orders, DATA_ORDER)
                        st.rerun()
                with c_btn2:
                    st.write(""); st.write("")
                    if st.button("❌ Hủy Món Này", type="secondary", use_container_width=True):
                        df_orders = df_orders[~((df_orders["Bàn"] == ban_xem_bill) & (df_orders["Món Ăn"] == mon_can_sua))]
                        save_data(df_orders, DATA_ORDER)
                        st.rerun()
            
            # Khung hóa đơn xem trước
            st.write("---")
            st.subheader("👀 Xem trước mẫu hóa đơn thực tế:")
            thời_gian_in = datetime.now().strftime('%d/%m/%Y %H:%M')
            phieu_text = f"====================================\n"
            phieu_text += f"        PHIẾU TÍNH TIỀN COFFEE      \n"
            phieu_text += f"------------------------------------\n"
            phieu_text += f" Vị trí: {ban_xem_bill}\n"
            phieu_text += f" Ngày: {thời_gian_in}\n"
            phieu_text += f"====================================\n"
            phieu_text += f" Tên Món       | SL | Thành Tiền\n"
            phieu_text += f"------------------------------------\n"
            for _, row in bill_ban.iterrows():
                ten_rut_gon = row['Món Ăn'][:14].ljust(14)
                phieu_text += f" {ten_rut_gon} | {row['Số Lượng']}  | {row['Thành Tiền']:,.0f} đ\n"
            phieu_text += f"------------------------------------\n"
            phieu_text += f" TỔNG CỘNG: {tong_bill:,.0f} VND\n"
            phieu_text += f"====================================\n"
            phieu_text += f"   CẢM ƠN QUÝ KHÁCH & HẸN GẶP LẠI   \n"
            phieu_text += f"===================================="
            st.code(phieu_text, language="text")
            
            # Nút bấm in và lưu dữ liệu
            if st.button(f"🖨️ XÁC NHẬN IN & THANH TOÁN", type="primary", use_container_width=True):
                # 1. Lưu đơn hàng vào lịch sử đối chiếu
                for _, row in bill_ban.iterrows():
                    new_history_row = pd.DataFrame([{"Thời Gian": thời_gian_in, "Bàn": row["Bàn"], "Món Ăn": row["Món Ăn"], "Giá": row["Giá"], "Số Lượng": row["Số Lượng"], "Thành Tiền": row["Thành Tiền"]}])
                    df_history = pd.concat([df_history, new_history_row], ignore_index=True)
                save_data(df_history, DATA_HISTORY)
                
                # 2. Lệnh in trình duyệt
                js_code = f"<script>var printWindow = window.open('', '', 'height=600,width=400');printWindow.document.write('<html><head><title>In Hoa Don</title></head><body>');printWindow.document.write('<pre style=\"font-family: monospace; font-size: 14px;\">' + `{phieu_text}` + '</pre>');printWindow.document.write('</body></html>');printWindow.document.close();printWindow.print();</script>"
                st.components.v1.html(js_code, height=0, width=0)
                
                # 3. Giải phóng bàn
                df_orders = df_orders[df_orders["Bàn"] != ban_xem_bill]
                save_data(df_orders, DATA_ORDER)
                st.toast(f"Đã thanh toán thành công!")
                st.rerun()
        else:
            st.info(f"Hiện tại **{ban_xem_bill}** đang trống, không có món ăn nào đang chạy.")

# ==============================================================================
# TRANG 2: TRANG THỐNG KÊ, ĐỐI CHIẾU VÀ XUẤT FILE FILE PDF/EXCEL
# ==============================================================================
elif chức_năng == "📊 Thống Kê & Xuất Dữ Liệu":
    st.title("📊 TRANG QUẢN LÝ LỊCH SỬ VÀ ĐỐI CHIẾU DOANH THU")
    
    if not df_history.empty:
        tổng_doanh_thu = df_history["Thành Tiền"].sum()
        tổng_ly_ban = df_history["Số Lượng"].sum()
        tổng_hoa_don = df_history["Thời Gian"].nunique()
        
        c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
        c_kpi1.metric("💰 TỔNG DOANH THU TÍCH LŨY", f"{tổng_doanh_thu:,.0f} VND")
        c_kpi2.metric("📦 TỔNG SỐ MÓN ĐÃ BÁN", f"{tổng_ly_ban:,} Món")
        c_kpi3.metric("🧾 TỔNG LƯỢT HÓA ĐƠN", f"{tổng_hoa_don:,} Lượt")
        
        st.write("---")
        st.subheader("📥 Xuất dữ liệu lưu trữ về máy tính")
        csv_data = df_history.to_csv(index=False).encode('utf-8-sig')
        st.download_button(label="📥 Tải File Báo Cáo Đối Chiếu (Dạng Excel/CSV)", data=csv_data, file_name=f"Bao_cao_doanh_thu.csv", mime="text/csv", use_container_width=True)
            
        st.subheader("📈 Biểu đồ món ăn được yêu thích nhất")
        mon_banchay = df_history.groupby("Món Ăn")["Số Lượng"].sum().sort_values(ascending=True)
        st.bar_chart(mon_banchay)
        
        st.subheader("📋 Nhật ký chi tiết tất cả các đơn hàng thành công")
        st.dataframe(df_history, use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có dữ liệu hóa đơn nào trong lịch sử.")
