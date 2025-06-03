from django.http import HttpResponseForbidden
from .models import AllowedIP, BlockedIPLog

class IPFirewallMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_ips = [ip.ip_address for ip in AllowedIP.objects.all()]
        remote_ip = self.get_client_ip(request)

        print("📌 요청한 클라이언트 IP:", remote_ip)
        print("✅ 현재 허용된 IP 목록:", allowed_ips)

        if remote_ip not in allowed_ips:
            BlockedIPLog.objects.create(ip_address=remote_ip, accessed_path=request.path)
            return HttpResponseForbidden(f"Access denied for IP: {remote_ip}")

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # IP가 여러 개일 수 있으므로 첫 번째 값 사용
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR') # 일반적인 경우
        return ip
