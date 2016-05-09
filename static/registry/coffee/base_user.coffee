registry.module('forms.user') unless registry.has('forms.user')

(registry.forms.user = (($) ->
   editables = $("input.editable");

   # End of Authenticator Class
   originals = {}
   changes = []
   auth = null

   editables.prop('readonly', true).addClass('no-input').each(->
      originals[@] = $(@).val();
   );

   createReversion = ->
      (elem, old) -> $(elem).val(old)

   revertChanges = ->
      c.revert() for c in changes
      changes = []

   handleFailedChanges = (changes) ->
      c.revert() for c in changes

   handleConfirmedChanges = (changes) ->
      originals[c.target] = c.new for c in changes

   commitChanges = ->
      return if changes.length == 0

      vex.dialog.confirm
         message: "Do you want to submit the current changes to the user profiles?"
         callback: (value) ->
            if not value then revertChanges()
            else
               auth.commitChanges(changes, (err, confirmed, failed) ->
                  handleConfirmedChanges(confirmed)
                  handleFailedChanges(failed)
                  changes = []
               )


   hookPermissions = (uuid) ->
      throw new Error('Cannot reassign editability!') if auth?

      auth = new Authenticator(uuid)

      applyReadonlyUnlessFocused = (editables, filterword, perm) ->
         editables.filter(-> $(@).data('auth-type') is filterword)
         .click(-> $(@).prop('readonly', false))
         .blur(-> $(@).prop('readonly', true))
         .change(->
           if $(@).val() is not originals[@]
               changes.push(new Change(@, $(@).val(), originals[@], createReversion(), perm))
         )
         .removeClass('no-input')

      auth.use((error, perms) ->
         for p in perms
            switch p
               when 'edit.personal'
                  applyReadonlyUnlessFocused(editables, 'personal', 'edit.personal')
               when 'edit.medical'
                  applyReadonlyUnlessFocused(editables, 'medical', 'edit.medical')
               when 'edit.insurance'
                  applyReadonlyUnlessFocused(editables, 'insurance', 'edit.insurance')

         return
      )

   return {
      hook: hookPermissions
      isAuthUser: (uuid) -> if auth? then auth.checkUser(uuid) else no
      updateUser: commitChanges
   })(jQuery))

(($, _) -> $ ->
   tabLinks = $("#tab-links")
   tabLinkListItems = tabLinks.find('li')
   innerTabLinks = $("#innertab-links")
   innerTabLinksListItems = innerTabLinks.find('li')

   # Top Level Tab Click Handling
   tabLinkListItems.click((event) ->
# Store reference to self and active and disable current active tab
      jSelf = $(@)
      active = tabLinkListItems.find('.active')
      active.removeClass('active')

      # Set self to active, hide tab content and fade in the tab
      # owned by self
      jSelf.addClass('active')
      $('.tab').hide()
      $(jSelf.find('a').attr('href')).fadeIn()

      # Prevent redirection to link
      registry.stopEventBehavior(event)
   )

   # Extremely similar to above
   innerTabLinksListItems.click((event) ->
      jSelf = $(@)
      active = innerTabLinksListItems.find('.active')

      active.removeClass('active')
      jSelf.addClass('active')

      $('.tab').hide()
      $(jSelf.find('a').attr('href')).fadeIn()

      registry.stopEventBehavior(event)
   )

   inbox = $("#inbox")
   checkAllBox = $("#checkAll")
   msgSender = $("#message_sender")
   msgDate = $("#message_date")
   msgTitle = $("#message_title")
   msgContent = $("#message_content")
   msgCreateForm = $("#msg-create-form-html")

   checkAllBox.change(-> $("input#msg-checkbox").prop('checked', $(@).prop('checked')))
   checkAllBox.on('msg:uncheck', -> checkAllBox.click() if checkAllBox.is(':checked'))

   uncheckHandler = -> checkAllBox.trigger('msg:uncheck') unless $(@).is(':checked')
   messageOpenHandler = ->
      jSelf = $(@)
      parentRow = jSelf.parent('tr')
      selected = parentRow.attr('href')
      uuid = parentRow.data('message-id')

      $.ajax
         url: "msg/#{uuid}"
         type: 'GET'
         success: (resp) ->
            sender = resp.sender['name']
            date = moment(resp['date']).format('MMMM Do YYYY [at] h:mm:ss a')
            title = resp['title']
            content = registry.escapeHtml(resp['content']).replace(/(?:\r\n|\r|\n)/g, '<br />')

            msgSender.text(sender)
            msgDate.text(date)
            msgTitle.text(title)
            msgContent.html(content)

            $(".tab").hide()
            $(selected).fadeIn()

   $('input#msg-checkbox').change(uncheckHandler)

   inbox.find("td").not('.check-box-wrapper').click(messageOpenHandler)

   $("#newMessage").click((event) ->
      form = msgCreateForm.clone()
      document.getElementById('msgCreation').reset()

      form.css("display", "block")
      form.find('span.help-inline').remove()

      vex.dialog.buttons.YES.text = 'Send'
      vex.dialog.open
         message: form
         callback: (data) ->
            return unless data

            vexContent = $('.vex-content')
            title = vexContent.find('#id_title').val()
            receiver = vexContent.find('#id_receiver').find(':selected').val()
            $.ajax
               url: '/msg'
               type: 'POST'
               data:
                  receiver: registry.escapeHtml(receiver)
                  content: vexContent.find('#id_content').val()
                  title: registry.escapeHtml(title)
               success: (resp) ->
                  vex.close()
                  return unless resp.success && registry.forms.user.isAuthUser(receiver)

                  tmpId = 'TEMP-MESSAGE-ID-FOR-CLICK'
                  time = moment(resp.timestamp).format('MMMM D, YYYY, h:mm a').replace(`/ am/g`, ' a.m.').replace(`/ pm/g`, ' p.m.')
                  inbox.find('tbody').prepend("""
                  <tr data-message-id="#{resp.id}" class="inbox-row" href="#tab7" id="#{tmpId}">
                     <td class="inboxBody check-box-wrapper">
                        <input id="msg-checkbox" type="checkbox"/>
                     </td>
                     <td class="inboxBody">#{resp.sender}</td>
                     <td class="inboxBody">#{title}</td>
                     <td class="inboxBody">#{time}</td>
                  </tr>
                  """)
                  tmp = $("##{tmpId}")
                  tmp.find('td').not('.check-box-wrapper').click(messageOpenHandler)
                  tmp.attr('id', null)
               failure: -> vex.close()
   )

   $("#id-delete-msg").click(->
      mIds = []
      inbox.find('input:checked').not('#checkAll').each(-> mIds.push $(@).parent('td').parent('tr').data('message-id'))
      return unless mIds.length > 0

      msgHandler = (messages, failures) ->
         messages = _.without(messages, failures)
         _.each(messages, (mId) -> $(".inbox-row[data-message-id='#{mId}'").remove())
         checkAllBox.trigger('msg:uncheck')

      $.ajax
         url: 'msg/' + mIds[0]
         type: 'DELETE'
         data:
            messages: mIds
         success: (resp) -> msgHandler(mIds, resp.fails)
   )

   $("#Dismiss").click(->
    $('#sysMessage')[0].style.display = 'none'
   )


   # TODO This may be re-worked, the constant fade is annoying
   buttonButtonsPresButtonsHandler = (evt) ->
      $('.tab').hide()
      $($(@).find('a').attr('href')).fadeIn()
      registry.stopEventBehavior(evt)

   $('#buttons').click(buttonButtonsPresButtonsHandler)
   $('#presbuttons').click(buttonButtonsPresButtonsHandler)
   $('#button').click(buttonButtonsPresButtonsHandler)

   # TODO Replace with update button
   $(window).bind('beforeunload', registry.forms.user.updateUser))(jQuery, _)