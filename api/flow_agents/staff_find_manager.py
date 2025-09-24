"""
Staff .find Manager - Sistema para Staff registrar nomes gratuitamente
Para uso no bootcamp presencial - conta 0x01cf0e2f2f715450 é STAFF
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import hashlib

class StaffFindManager:
    """
    Sistema especial para Staff gerenciar nomes .find no bootcamp
    """

    def __init__(self):
        self.staff_account = "0x01cf0e2f2f715450"  # Conta do chat/staff
        self.testnet_contracts = {
            "FIND": "0x35717efbbce11c74",
            "Profile": "0x35717efbbce11c74",
            "FlowToken": "0x7e60df042a9c0868"
        }
        self.registered_participants = []
        self.event_id = "bootcamp2024"

    # ===================================
    # CONTRATO ESPECIAL PARA STAFF
    # ===================================

    def deploy_staff_registry_contract(self) -> str:
        """
        Deploy de contrato que permite Staff registrar nomes gratuitamente
        """
        return f'''
        import FIND from {self.testnet_contracts["FIND"]}
        import FlowToken from {self.testnet_contracts["FlowToken"]}

        pub contract BootcampFindRegistry {{

            // Eventos
            pub event StaffAuthorized(address: Address)
            pub event NameRegisteredByStaff(name: String, participant: Address, staff: Address)
            pub event BatchRegistrationComplete(count: Int, staff: Address)
            pub event FreeNameMinted(name: String, eventId: String)

            // Estado
            pub var authorizedStaff: {{Address: Bool}}
            pub var registeredNames: {{String: Address}}
            pub var eventNames: {{String: [String]}}  // eventId -> lista de nomes
            pub var totalFreeRegistrations: UInt64

            // Recurso de Staff Admin
            pub resource StaffAdmin {{
                pub fun registerFreeNameForParticipant(
                    participantName: String,
                    participantAddress: Address,
                    eventId: String
                ): Bool {{
                    // Cria nome único para o evento
                    let uniqueName = participantName
                        .concat("-")
                        .concat(eventId)
                        .concat("-")
                        .concat(BootcampFindRegistry.totalFreeRegistrations.toString())

                    // Verifica se nome já existe
                    if BootcampFindRegistry.registeredNames[uniqueName] != nil {{
                        return false
                    }}

                    // Registra nome (seria integrado com FIND real em produção)
                    BootcampFindRegistry.registeredNames[uniqueName] = participantAddress

                    // Adiciona à lista do evento
                    if BootcampFindRegistry.eventNames[eventId] == nil {{
                        BootcampFindRegistry.eventNames[eventId] = []
                    }}
                    BootcampFindRegistry.eventNames[eventId]!.append(uniqueName)

                    // Incrementa contador
                    BootcampFindRegistry.totalFreeRegistrations =
                        BootcampFindRegistry.totalFreeRegistrations + 1

                    // Emite evento
                    emit NameRegisteredByStaff(
                        name: uniqueName,
                        participant: participantAddress,
                        staff: self.owner?.address ?? 0x0
                    )

                    emit FreeNameMinted(name: uniqueName, eventId: eventId)

                    return true
                }}

                pub fun batchRegisterNames(
                    participants: [{{name: String, address: Address}}],
                    eventId: String
                ): [String] {{
                    let registeredNames: [String] = []

                    for participant in participants {{
                        if self.registerFreeNameForParticipant(
                            participantName: participant.name,
                            participantAddress: participant.address,
                            eventId: eventId
                        ) {{
                            registeredNames.append(participant.name)
                        }}
                    }}

                    emit BatchRegistrationComplete(
                        count: registeredNames.length,
                        staff: self.owner?.address ?? 0x0
                    )

                    return registeredNames
                }}
            }}

            // Verifica se endereço é staff autorizado
            pub fun isAuthorizedStaff(address: Address): Bool {{
                return self.authorizedStaff[address] ?? false
            }}

            // Obtém nome registrado para endereço
            pub fun getRegisteredName(address: Address): String? {{
                for name in self.registeredNames.keys {{
                    if self.registeredNames[name] == address {{
                        return name
                    }}
                }}
                return nil
            }}

            // Lista nomes de um evento
            pub fun getEventNames(eventId: String): [String] {{
                return self.eventNames[eventId] ?? []
            }}

            // Cria recurso de admin para staff
            pub fun createStaffAdmin(): @StaffAdmin {{
                return <- create StaffAdmin()
            }}

            init() {{
                self.authorizedStaff = {{
                    {self.staff_account}: true  // Conta do chat é staff
                }}
                self.registeredNames = {{}}
                self.eventNames = {{}}
                self.totalFreeRegistrations = 0

                // Autoriza conta inicial
                emit StaffAuthorized(address: {self.staff_account})

                // Salva admin resource
                self.account.save(
                    <- create StaffAdmin(),
                    to: /storage/BootcampStaffAdmin
                )
            }}
        }}
        '''

    # ===================================
    # TRANSAÇÕES PARA STAFF
    # ===================================

    def staff_register_single_name(self, participant_name: str, participant_address: str) -> str:
        """
        Transação para Staff registrar um nome gratuitamente
        """
        return f'''
        import BootcampFindRegistry from {self.staff_account}
        import FIND from {self.testnet_contracts["FIND"]}

        transaction(participantName: String, participantAddress: Address) {{
            let staffAdmin: &BootcampFindRegistry.StaffAdmin

            prepare(staff: AuthAccount) {{
                // Verifica se é staff autorizado
                assert(
                    BootcampFindRegistry.isAuthorizedStaff(address: staff.address),
                    message: "Apenas staff autorizado pode registrar nomes!"
                )

                // Pega referência do admin
                self.staffAdmin = staff.borrow<&BootcampFindRegistry.StaffAdmin>(
                    from: /storage/BootcampStaffAdmin
                ) ?? panic("Staff admin resource não encontrado")
            }}

            execute {{
                // Registra nome gratuitamente
                let success = self.staffAdmin.registerFreeNameForParticipant(
                    participantName: participantName,
                    participantAddress: participantAddress,
                    eventId: "bootcamp2024"
                )

                if success {{
                    log("✅ Nome registrado com sucesso para ".concat(participantName))
                }} else {{
                    log("❌ Falha ao registrar nome")
                }}
            }}
        }}
        '''

    def staff_batch_register_names(self, participants: List[Dict]) -> str:
        """
        Registra múltiplos nomes de uma vez (check-in em massa)
        """
        return f'''
        import BootcampFindRegistry from {self.staff_account}

        transaction(participants: [{{name: String, address: Address}}]) {{
            let staffAdmin: &BootcampFindRegistry.StaffAdmin

            prepare(staff: AuthAccount) {{
                assert(
                    BootcampFindRegistry.isAuthorizedStaff(address: staff.address),
                    message: "Apenas staff autorizado!"
                )

                self.staffAdmin = staff.borrow<&BootcampFindRegistry.StaffAdmin>(
                    from: /storage/BootcampStaffAdmin
                ) ?? panic("Staff admin não encontrado")
            }}

            execute {{
                let registered = self.staffAdmin.batchRegisterNames(
                    participants: participants,
                    eventId: "bootcamp2024"
                )

                log("Registrados ".concat(registered.length.toString()).concat(" nomes"))
                log(registered)
            }}
        }}
        '''

    # ===================================
    # COMANDOS DE CHAT PARA STAFF
    # ===================================

    def process_staff_chat_command(self, message: str, sender_address: str) -> Dict:
        """
        Processa comandos de chat do Staff
        """
        # Verifica se é staff
        if sender_address != self.staff_account:
            return {
                "success": False,
                "error": "Apenas staff autorizado pode usar estes comandos",
                "your_address": sender_address,
                "staff_address": self.staff_account
            }

        message_lower = message.lower()

        # COMANDO: Registrar nome individual
        if message_lower.startswith("/registrar"):
            # Formato: /registrar joão 0x123...
            parts = message.split()
            if len(parts) >= 3:
                name = parts[1]
                address = parts[2]

                # Gera nome único
                unique_name = f"{name}-{self.event_id}-{len(self.registered_participants)}"

                self.registered_participants.append({
                    "name": unique_name,
                    "original": name,
                    "address": address,
                    "timestamp": datetime.now().isoformat(),
                    "registered_by": sender_address
                })

                return {
                    "success": True,
                    "action": "register_single",
                    "name": f"{unique_name}.find",
                    "participant": name,
                    "address": address,
                    "message": f"✅ Registrado: {unique_name}.find para {address}",
                    "total_registered": len(self.registered_participants)
                }

        # COMANDO: Registrar em lote
        elif message_lower.startswith("/lote"):
            # Formato: /lote joão:0x123,maria:0x456,pedro:0x789
            parts = message.split(maxsplit=1)
            if len(parts) > 1:
                batch_data = parts[1]
                participants = []

                for entry in batch_data.split(","):
                    if ":" in entry:
                        name, address = entry.split(":", 1)
                        unique_name = f"{name.strip()}-{self.event_id}-{len(self.registered_participants)}"
                        participants.append({
                            "name": unique_name,
                            "original": name.strip(),
                            "address": address.strip()
                        })
                        self.registered_participants.append({
                            "name": unique_name,
                            "original": name.strip(),
                            "address": address.strip(),
                            "timestamp": datetime.now().isoformat(),
                            "registered_by": sender_address
                        })

                return {
                    "success": True,
                    "action": "batch_register",
                    "count": len(participants),
                    "participants": participants,
                    "message": f"✅ Registrados {len(participants)} nomes em lote!",
                    "total_registered": len(self.registered_participants)
                }

        # COMANDO: Listar registrados
        elif message_lower.startswith("/listar"):
            return {
                "success": True,
                "action": "list",
                "participants": self.registered_participants[-10:],  # Últimos 10
                "total": len(self.registered_participants),
                "message": f"📋 Total de {len(self.registered_participants)} participantes registrados"
            }

        # COMANDO: Info do sistema
        elif message_lower.startswith("/info"):
            return {
                "success": True,
                "action": "info",
                "event": self.event_id,
                "staff_account": self.staff_account,
                "total_registered": len(self.registered_participants),
                "ready_for_quiz": True,
                "message": "🎮 Sistema pronto para Quiz Race!"
            }

        # COMANDO: Gerar QR Code para check-in
        elif message_lower.startswith("/qrcode"):
            # Gera dados para QR code
            qr_data = {
                "event": self.event_id,
                "staff": self.staff_account,
                "register_url": f"https://quiz.flow/register?event={self.event_id}",
                "instructions": "Escaneie para registrar seu nome .find grátis!"
            }

            return {
                "success": True,
                "action": "qrcode",
                "qr_data": json.dumps(qr_data),
                "message": "📱 QR Code gerado para check-in!",
                "display_text": f"BOOTCAMP FLOW 2024\nRegistre seu nome .find\nGRÁTIS!"
            }

        # Comando não reconhecido
        return {
            "success": False,
            "error": "Comando não reconhecido",
            "help": """
Comandos disponíveis para Staff:
/registrar [nome] [endereço] - Registra um participante
/lote nome1:0x1,nome2:0x2 - Registra vários de uma vez
/listar - Lista últimos registrados
/info - Informações do sistema
/qrcode - Gera QR para check-in
            """,
            "your_role": "STAFF AUTORIZADO ✅"
        }

    # ===================================
    # INTERFACE PARA CHAT
    # ===================================

    def generate_checkin_interface(self) -> str:
        """
        Gera interface HTML para check-in via chat
        """
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Check-in Bootcamp Flow 2024</title>
            <style>
                body { font-family: Arial; padding: 20px; background: #1a1a2e; color: #fff; }
                .container { max-width: 600px; margin: 0 auto; }
                .header { text-align: center; padding: 20px; background: #0f4c75; border-radius: 10px; }
                .form-group { margin: 20px 0; }
                input { width: 100%; padding: 10px; font-size: 16px; border-radius: 5px; border: none; }
                button { width: 100%; padding: 15px; background: #3282b8; color: white; border: none;
                         border-radius: 5px; font-size: 18px; cursor: pointer; }
                button:hover { background: #45a0e6; }
                .registered { background: #28a745; padding: 10px; margin: 10px 0; border-radius: 5px; }
                .count { font-size: 48px; text-align: center; color: #3282b8; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎮 Check-in Quiz Race</h1>
                    <p>Bootcamp Flow Blockchain 2024</p>
                    <div class="count" id="count">0</div>
                    <p>Participantes Registrados</p>
                </div>

                <div class="form-group">
                    <input type="text" id="name" placeholder="Nome do participante">
                </div>

                <div class="form-group">
                    <input type="text" id="address" placeholder="Endereço Flow (opcional)">
                </div>

                <button onclick="register()">
                    REGISTRAR NOME .FIND GRÁTIS
                </button>

                <div id="registered-list"></div>
            </div>

            <script>
                let count = 0;

                async function register() {
                    const name = document.getElementById('name').value;
                    const address = document.getElementById('address').value || generateAddress();

                    if (!name) {
                        alert('Digite o nome do participante!');
                        return;
                    }

                    // Chama API
                    const response = await fetch('/api/staff/register', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            command: `/registrar ${name} ${address}`,
                            sender: '0x01cf0e2f2f715450'
                        })
                    });

                    const result = await response.json();

                    if (result.success) {
                        count++;
                        document.getElementById('count').textContent = count;

                        const div = document.createElement('div');
                        div.className = 'registered';
                        div.textContent = `✅ ${result.name} registrado!`;
                        document.getElementById('registered-list').prepend(div);

                        // Limpa campos
                        document.getElementById('name').value = '';
                        document.getElementById('address').value = '';
                    }
                }

                function generateAddress() {
                    // Gera endereço temporário
                    return '0x' + Math.random().toString(16).substr(2, 16);
                }
            </script>
        </body>
        </html>
        '''

# ===================================
# EXEMPLO DE USO
# ===================================

def example_staff_usage():
    """
    Exemplo de uso pelo Staff no evento
    """
    staff = StaffFindManager()

    print("=" * 60)
    print("🎯 STAFF .FIND MANAGER - BOOTCAMP 2024")
    print("=" * 60)

    # Simula comandos do chat
    commands = [
        "/info",
        "/registrar joão 0x123456",
        "/registrar maria 0x789abc",
        "/lote pedro:0xaaa,ana:0xbbb,carlos:0xccc",
        "/listar",
        "/qrcode"
    ]

    for cmd in commands:
        print(f"\n📝 Comando: {cmd}")
        result = staff.process_staff_chat_command(cmd, staff.staff_account)
        print(f"✅ Resultado: {result['message']}")

    print("\n" + "=" * 60)
    print("RESUMO DO CHECK-IN")
    print("=" * 60)
    print(f"Total registrado: {len(staff.registered_participants)}")
    print("Participantes prontos para Quiz Race!")

    # Mostra contrato
    print("\n" + "=" * 60)
    print("CONTRATO PARA DEPLOY")
    print("=" * 60)
    contract = staff.deploy_staff_registry_contract()
    print("Contrato BootcampFindRegistry pronto para deploy!")

if __name__ == "__main__":
    example_staff_usage()