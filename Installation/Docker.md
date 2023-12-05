# Instalacion de Docker en Debian
- Puedes seguir los pasos de este tutorial para instalar Docker en Debian o puedes seguir la documentacion oficial de Docker para instalarlo en tu sistema operativo [Docker](https://docs.docker.com/engine/install/debian/)🐳

## Primer paso
- Vamos a configurar el repositorio de apt de Docker.📦
```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
# Add the repository to Apt sources:
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

## Segundo paso
- Despues vamos a instalar la ultima version de Docker ⬇️
```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
docker pull hello-world
```

## Tercer paso
- Ejecutamos el siguiente comando para verificar que Docker se instaló correctamente: ✅
```bash
sudo service docker start
sudo docker run hello-world
```

## Verificacion
- Si todo sale bien, debería aparecer el siguiente mensaje:✔️
```bash
Hello from Docker!
This message shows that your installation appears to be working correctly.
```
