"""
Orders Views - Use appropriate view type for each case

File: views.py
Author: Anthony Bañon
Created: 2025-12-05
Last Updated: 2025-12-05
"""

from rest_framework import generics, viewsets, status, mixins
from rest_framework.views import APIView
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Order, OrderItem, Payment
from .serializers import *
from .services import OrderService, PaymentService, AdminOrderService, BusinessException
from .constants import *


##### User Order Views (ViewSet for comprehensive order operations) #####

class OrderViewSet(viewsets.ViewSet):
    """✅ ViewSet for user order operations"""
    permission_classes = [IsAuthenticated]
    
    def _get_order_service(self):
        return OrderService()
    
    def _get_payment_service(self):
        return PaymentService()
    
    # Swagger documentation workaround
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.all()
    
    def list(self, request):
        """✅ Get all orders for current user"""
        order_service = self._get_order_service()
        orders = order_service.get_user_orders(request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """✅ Get specific order details"""
        order_service = self._get_order_service()
        
        try:
            order = order_service.get_order_by_id(request.user, pk)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def cancel(self, request, pk=None):
        """✅ Cancel an order (complex logic in service)"""
        serializer = OrderCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order_service = self._get_order_service()
        
        try:
            order = order_service.cancel_order(
                request.user,
                pk,
                serializer.validated_data.get('reason', '')
            )
            
            return Response({
                'message': SUCCESS_ORDER_CANCELLED,
                'data': OrderSerializer(order).data
            })
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def status_history(self, request, pk=None):
        """✅ Get order status history"""
        order_service = self._get_order_service()
        
        try:
            order = order_service.get_order_by_id(request.user, pk)
            history = order_service.get_order_status_history(order)
            return Response(history)
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def payment_info(self, request, pk=None):
        """✅ Get payment information for an order"""
        order_service = self._get_order_service()
        payment_service = self._get_payment_service()
        
        try:
            order = order_service.get_order_by_id(request.user, pk)
            payment = payment_service.get_order_payment(order)
            
            if payment:
                serializer = PaymentSerializer(payment)
                return Response(serializer.data)
            else:
                return Response({
                    'message': 'No payment found for this order',
                    'data': None
                })
                
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


##### Payment Views (APIView for complex payment logic) #####

class CreatePaymentView(APIView):
    """✅ APIView for creating payment for an order"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(request_body=PaymentCreateSerializer)
    @transaction.atomic
    def post(self, request, order_id):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order_service = OrderService()
        payment_service = PaymentService()
        
        try:
            # Get order with permission check
            order = order_service.get_order_by_id(request.user, order_id)
            
            # Check if order can have payment
            if order.status != ORDER_STATUS_PENDING:
                return Response(
                    {'error': 'Cannot create payment for non-pending order'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create payment
            payment = payment_service.create_payment(
                order,
                serializer.validated_data['payment_method']
            )
            
            return Response({
                'message': SUCCESS_PAYMENT_CREATED,
                'data': {
                    'payment_id': payment.id,
                    'order_id': order.id,
                    'amount': payment.amount,
                    'payment_method': payment.payment_method,
                    'status': payment.status,
                    # In real implementation, you would return payment gateway URL here
                    'payment_url': self._generate_payment_url(payment)
                }
            })
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def _generate_payment_url(self, payment):
        """Helper method to generate payment gateway URL"""
        # This would integrate with Stripe/MercadoPago API
        # For now, return a mock URL
        return f"/api/payments/{payment.id}/process/"


class PaymentWebhookView(APIView):
    """✅ APIView for payment webhooks/callbacks (external services)"""
    permission_classes = [AllowAny]  # Webhooks don't require authentication
    
    @swagger_auto_schema(request_body=PaymentUpdateSerializer)
    @transaction.atomic
    def post(self, request, payment_id):
        serializer = PaymentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment_service = PaymentService()
        
        try:
            payment = Payment.objects.get(id=payment_id)
            order = payment.order
            
            payment, order = payment_service.update_payment_status(
                order,
                serializer.validated_data.get('transaction_id', ''),
                serializer.validated_data['status']
            )
            
            return Response({
                'message': SUCCESS_PAYMENT_UPDATED,
                'data': {
                    'payment_id': payment.id,
                    'order_id': order.id,
                    'order_status': order.status,
                    'payment_status': payment.status
                }
            })
            
        except (Payment.DoesNotExist, BusinessException) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


##### Admin Order Views (for staff users) #####

class AdminOrderViewSet(viewsets.ViewSet):
    """✅ ViewSet for admin order management"""
    permission_classes = [IsAdminUser]
    
    def _get_admin_service(self):
        return AdminOrderService()
    
    def list(self, request):
        """✅ Get all orders with filters"""
        admin_service = self._get_admin_service()
        
        # Get filters from query params
        filters = {
            'status': request.query_params.get('status'),
            'date_from': request.query_params.get('date_from'),
            'date_to': request.query_params.get('date_to'),
        }
        
        orders = admin_service.get_all_orders(filters)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put'])
    @transaction.atomic
    def update_status(self, request, pk=None):
        """✅ Admin updates order status"""
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        admin_service = self._get_admin_service()
        
        try:
            order = admin_service.update_order_status(
                pk,
                serializer.validated_data['status']
            )
            
            return Response({
                'message': SUCCESS_ORDER_STATUS_UPDATED,
                'data': OrderSerializer(order).data
            })
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """✅ Get order statistics"""
        from django.db.models import Count, Sum, Avg
        from django.utils import timezone
        from datetime import timedelta
        
        # Calculate statistics
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        avg_order_value = Order.objects.aggregate(Avg('total_amount'))['total_amount__avg'] or 0
        
        # Last 30 days statistics
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_orders = Order.objects.filter(created_at__gte=thirty_days_ago)
        
        recent_count = recent_orders.count()
        recent_revenue = recent_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Status distribution
        status_distribution = Order.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        return Response({
            'overall': {
                'total_orders': total_orders,
                'total_revenue': float(total_revenue),
                'average_order_value': float(avg_order_value)
            },
            'last_30_days': {
                'orders_count': recent_count,
                'revenue': float(recent_revenue)
            },
            'status_distribution': list(status_distribution)
        })