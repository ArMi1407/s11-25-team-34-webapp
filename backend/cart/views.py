"""
Cart Views - Use appropriate view type for each case

File: views.py
Author: [Tu Nombre]
Created: 2025-12-01
"""

from rest_framework import generics, viewsets, status, mixins
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction

from .models import Cart, CartItem
from .serializers import *
from .services import CartService, BusinessException
from .constants import *


##### Cart Views (ViewSet for comprehensive cart operations) #####

class CartViewSet(viewsets.ViewSet):
    """✅ ViewSet for all cart operations"""
    permission_classes = [AllowAny]  # Allow both authenticated and guest users
    
    # Swagger documentation workaround
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        return Cart.objects.all()

    def _get_cart_service(self):
        return CartService()

    def list(self, request):
        """✅ Get current cart with all items"""
        cart_service = self._get_cart_service()
        cart = cart_service.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @swagger_auto_schema(request_body=AddToCartSerializer)
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """✅ Add item to cart (complex logic in service)"""
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            cart_service = self._get_cart_service()
            cart_item = cart_service.add_to_cart(
                request,
                serializer.validated_data['product_id'],
                serializer.validated_data['quantity']
            )
            
            cart = cart_item.cart
            return Response({
                'message': 'Item added to cart successfully',
                'data': {
                    'cart_item': CartItemSerializer(cart_item).data,
                    'cart_summary': {
                        'total_items': cart.total_items,
                        'total_price': cart.total_price,
                        'total_carbon_footprint': cart.total_carbon_footprint
                    }
                }
            })
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """✅ Clear all items from cart (simple logic in service)"""
        cart_service = self._get_cart_service()
        cart_service.clear_cart(request)
        
        return Response({
            'message': 'Cart cleared successfully',
            'data': {
                'cart_summary': {
                    'total_items': 0,
                    'total_price': 0,
                    'total_carbon_footprint': 0
                }
            }
        })


class CartItemViewSet(viewsets.GenericViewSet,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.RetrieveModelMixin):
    """RESTful handler for cart items at /cart/items/<id>/"""

    
    permission_classes = [AllowAny]

    def get_queryset(self):
        service = CartService()
        cart = service.get_cart(self.request)
        return CartItem.objects.filter(cart=cart)
    
    def get_serializer_class(self):
        # Swagger & DRF correctly handle request bodies depending on action
        if self.action in ["update", "partial_update"]:
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        pk = kwargs.get("pk")
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        try:
            service = CartService()
            cart_item = service.update_cart_item(request, pk, serializer.validated_data["quantity"])
            cart = cart_item.cart

            return Response({
                "message": "Cart item updated successfully",
                "data": {
                    "cart_item": CartItemSerializer(cart_item).data,
                    "cart_summary": {
                        "total_items": cart.total_items,
                        "total_price": cart.total_price,
                        "total_carbon_footprint": cart.total_carbon_footprint
                    }
                }
            })

        except BusinessException as e:
            return Response({"error": str(e)}, status=400)

    @transaction.atomic
    def destroy(self, request, pk=None):
        try:
            service = CartService()
            service.remove_from_cart(request, pk)

            cart = service.get_cart(request)
            return Response({
                "message": "Item removed from cart",
                "data": {
                    "cart_summary": {
                        "total_items": cart.total_items,
                        "total_price": cart.total_price,
                        "total_carbon_footprint": cart.total_carbon_footprint
                    }
                }
            })

        except BusinessException as e:
            return Response({"error": str(e)}, status=400)


##### Checkout View (APIView for complex checkout logic) #####

class CheckoutView(APIView):
    """✅ APIView for complex checkout logic"""
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(request_body=CheckoutSerializer)
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            cart_service = CartService()
            order = cart_service.checkout(
                request,
                serializer.validated_data['shipping_address']
            )
            
            return Response({
                'message': 'Order created successfully',
                'data': {
                    'order_number': order.order_number,
                    'total_amount': order.total_amount,
                    'total_carbon_footprint': order.total_carbon_footprint,
                    'status': order.status,
                    'order_id': order.id
                }
            }, status=status.HTTP_201_CREATED)
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


##### Cart Merge View (for post-login cart merging) #####

class MergeCartView(APIView):
    """✅ APIView for merging guest cart with user cart after login"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(operation_description="Merge guest cart with user cart after login")
    def post(self, request):
        old_key = request.session.get("old_session_key")
        
        if not old_key:
            return Response({'error': 'No anonymous cart to merge'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart_service = CartService()
            cart, warnings = cart_service.merge_carts(request.user, old_key)
            # Clean up old session key
            request.session.pop("old_session_key", None)

            response_data = {
                'message': 'Cart merged successfully',
                'data': CartSerializer(cart).data
            }
            if warnings:
                response_data['warnings'] = warnings
            
            return Response(response_data)
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
