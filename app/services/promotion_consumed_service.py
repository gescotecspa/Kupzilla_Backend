from app.models.promotion_consumed import PromotionConsumed
from app.models.promotion import Promotion
from app.models.user import User
from app.models.status import Status  
from app import db

class PromotionConsumedService:

    @staticmethod
    def get_promotion_consumed_by_id(id):
        return PromotionConsumed.query.get(id)

    @staticmethod
    def get_all_promotion_consumeds():
        return PromotionConsumed.query.all()

    @staticmethod
    def create_promotion_consumed(data):
        try:
            promotion = Promotion.query.get(data['promotion_id'])
            if not promotion:
                raise Exception("Promotion not found")
            
            # Verificar la cantidad solicitada
            quantity_to_consume = data.get('quantity_consumed', 1)
            
            # Validar si la promoción tiene un límite de consumo (available_quantity)
            if promotion.available_quantity is not None:
                # Verificar si hay suficiente cantidad disponible
                if promotion.available_quantity < quantity_to_consume:
                    raise ValueError("Insufficient available quantity for this promotion")
                
                # Descontar la cantidad disponible
                promotion.available_quantity -= quantity_to_consume
            
            # Sumar la cantidad consumida
            promotion.consumed_quantity += quantity_to_consume
            
            # Crear un nuevo registro de promoción consumida
            new_promotion_consumed = PromotionConsumed(
                user_id=data['user_id'],
                promotion_id=data['promotion_id'],
                status_id=data['status_id'],
                quantity_consumed=quantity_to_consume,
                amount_consumed=data.get('amount_consumed'),
                consumption_date=data.get('consumption_date'),
                description=data.get('description'),
                payment_method=data.get('payment_method')
            )
            
            # Guardar el registro de consumo y actualizar la promoción
            db.session.add(new_promotion_consumed)
            db.session.commit()
            
            return new_promotion_consumed
        
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def update_promotion_consumed(id, data):
        # Obtener el objeto de promoción consumida a actualizar
        # print("i y data______",id, data)
        promotion_consumed = PromotionConsumed.query.get(id)
        # print("promotion_consumed buscada",promotion_consumed)
        if not promotion_consumed:
            return None

        # Actualizar los campos de la promoción consumida según los datos proporcionados
        if 'user_id' in data:
            promotion_consumed.user_id = data['user_id']
        if 'promotion_id' in data:
            promotion_consumed.promotion_id = data['promotion_id']
        if 'status_id' in data:
            new_status_id = data['status_id']
            # Verificar si el nuevo estado es "deleted" o "cancelled"
            new_status = Status.query.get(new_status_id)
            print("nuevo status", new_status)
            if new_status and new_status.name in ['deleted', 'cancelled']:
                # Ajustar la cantidad disponible de la promoción
                if promotion_consumed.promotion_id:
                    promotion = Promotion.query.get(promotion_consumed.promotion_id)
                    if promotion:
                        # Revertir la cantidad consumida de la promoción
                        if promotion.available_quantity is not None:
                            # Revertir la cantidad consumida de la promoción
                            promotion.available_quantity += promotion_consumed.quantity_consumed
                        promotion.consumed_quantity -=  promotion_consumed.quantity_consumed
                        db.session.commit()

            # Actualizar el estado
            promotion_consumed.status_id = new_status_id

        if 'quantity_consumed' in data:
            # Si la cantidad consumida cambia, ajustar la cantidad disponible de la promoción
            old_quantity = promotion_consumed.quantity_consumed
            print("old_quantity_____________",old_quantity)
            new_quantity = data['quantity_consumed']
            if promotion_consumed.promotion_id:
                promotion = Promotion.query.get(promotion_consumed.promotion_id)
                print("promocion buscada",promotion)
                if promotion:
                    quantity_difference = old_quantity - new_quantity
                    
                    # Si available_quantity no es None, verificar que no se quede negativo
                    if promotion.available_quantity is not None:
                        if promotion.available_quantity + quantity_difference < 0:
                            raise ValueError("No hay suficientes promociones disponibles. No se puede consumir más de lo que hay disponible.")
                        
                        promotion.available_quantity += quantity_difference

                    # Siempre ajustar consumed_quantity, independientemente del valor de available_quantity
                    promotion.consumed_quantity += (new_quantity - old_quantity)

                    # Confirmar los cambios en la base de datos
                    db.session.commit()

            # Actualizar la cantidad consumida
            promotion_consumed.quantity_consumed = new_quantity

        if 'amount_consumed' in data:
            promotion_consumed.amount_consumed = data['amount_consumed']
        if 'consumption_date' in data:
            promotion_consumed.consumption_date = data['consumption_date']
        if 'description' in data:
            promotion_consumed.description = data['description']
        if 'payment_method' in data:
            promotion_consumed.payment_method = data['payment_method']
            
        db.session.commit()
        return promotion_consumed


    @staticmethod
    def delete_promotion_consumed(id):
        promotion_consumed = PromotionConsumed.query.get(id)
        if promotion_consumed:
            db.session.delete(promotion_consumed)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_promotion_consumeds_by_partner(partner_id):
        """
        Devuelve todas las promociones consumidas filtradas por partner_id.
        """
        # Realiza un JOIN entre la tabla de promociones y la tabla de promociones consumidas
        promotions_consumed = db.session.query(PromotionConsumed).join(Promotion).filter(Promotion.partner_id == partner_id).all()

        return promotions_consumed