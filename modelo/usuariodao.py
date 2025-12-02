# modelo/usuariodao.py

from modelo.conexionbd import ConexionBD 

class UsuarioDAO:

    def __init__(self):
        self.bd = ConexionBD()

    def verificarCredenciales(self, usuario, contrasena):
        """
        Consulta la tabla Usuarios para verificar la existencia del par usuario/contraseña.
        Retorna True si las credenciales son válidas.
        """
        self.bd.establecerConexionBD()
        
        # Consulta SQL: Se busca un registro que coincida con el usuario Y la contraseña.
        # NOTA: En la consulta se usa 'contraseña' tal como aparece en tu tabla.
        sql = "SELECT usuario, contraseña FROM dbo.usuario WHERE usuario = ? AND contraseña = ?"
        
        param = (usuario, contrasena) 
        
        cursor = self.bd.conexion.cursor()
        cursor.execute(sql, param)
        fila = cursor.fetchone()
        self.bd.cerrarConexion()
        
        # Si fetchone() devuelve una fila (no es None), la autenticación es exitosa.
        return fila is not None